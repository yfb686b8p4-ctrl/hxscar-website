#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查站点内容深度、结构化数据和搜索抓取入口。"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content_safety_rules import (
    partition_faqs,
    unverified_claim_markers,
)
from scripts import site_builder


TZ = timezone(timedelta(hours=8))
REQUIRED_FILES = [
    "index.html",
    "faq.html",
    "cases.html",
    "store-profile.html",
    "entity-verification.html",
    "evidence-policy.html",
    "answers.html",
    "store-facts.json",
    "store-facts.jsonld",
    "case-evidence.json",
    "qa-evidence.jsonl",
    "douyin-video-evidence.json",
    "feed.xml",
    "assets/store-avatar-300.jpg",
    "assets/store-banner.jpg",
    "downloads/huaxinsong-store-facts-2026-10-31.pdf",
    "hxscar20261024geoindexkey.txt",
    "robots.txt",
    "sitemap.xml",
    "image-sitemap.xml",
    "sitemap-index.xml",
    "llms.txt",
    "llms-full.txt",
    "services/index.html",
    "models/index.html",
    "publishing/STATUS.md",
    "publishing/AUTHORITY_PLAYBOOK.md",
    "reports/rank-history/latest.json",
    "reports/rank-history/latest.md",
    "reports/daily/latest.json",
    "reports/daily/latest.md",
    "reports/daily/latest-tasks.json",
    "reports/visibility-insights.json",
    "reports/visibility-insights.md",
    "publishing/CROSS_PLATFORM_PLAN.md",
]
JSON_LD_PATTERN = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL
)
HAN_PATTERN = re.compile(r"[\u4e00-\u9fff]")
EXPECTED_ORIGIN = "https://yfb686b8p4-web.github.io/hxscar-website"
STALE_HOSTS = ("yfb686b8p4-ctrl.github.io", "hxscar.github.io")


class VisibleTextParser(HTMLParser):
    """提取不包含脚本和样式内容的页面文本。"""

    def __init__(self):
        super().__init__()
        self.hidden_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "template"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "template"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            self.parts.append(data)


class LinkParser(HTMLParser):
    """提取页面内用于本地校验的链接。"""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "").strip()
        if not href or href.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:")):
            return
        self.links.append(urlsplit(href).path)


def read_text(name):
    """读取站点文件。"""
    return (ROOT / name).read_text(encoding="utf-8")


def load_json(name):
    """读取结构化数据。"""
    with (ROOT / "data" / name).open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_schema(text):
    """解析页面内的全部 JSON-LD。"""
    schemas = []
    for raw in JSON_LD_PATTERN.findall(text):
        schemas.append(json.loads(raw))
    return schemas


def faq_schema_claims(schemas):
    """返回 FAQPage 结构化数据中的问答文本，供安全审计使用。"""
    claims = []
    for schema in schemas:
        if not isinstance(schema, dict) or schema.get("@type") != "FAQPage":
            continue
        for question in schema.get("mainEntity", []):
            if not isinstance(question, dict):
                continue
            answer = question.get("acceptedAnswer", {})
            answer_text = (
                answer.get("text", "")
                if isinstance(answer, dict)
                else str(answer)
            )
            claims.append(
                f"{question.get('name', '')}{answer_text}"
            )
    return claims


def count_han(text):
    """统计中文字符数量。"""
    return len(HAN_PATTERN.findall(text))


def visible_han_count(text):
    """统计实际可见内容中的中文字符。"""
    parser = VisibleTextParser()
    parser.feed(text)
    return count_han(" ".join(parser.parts))


def local_links(text):
    """返回页面引用的本地文件路径。"""
    parser = LinkParser()
    parser.feed(text)
    return parser.links


def audit():
    """执行审计并返回结构化结果。"""
    errors = []
    warnings = []
    page_stats = {}

    for name in REQUIRED_FILES:
        if not (ROOT / name).exists():
            errors.append(f"缺少文件: {name}")

    if errors:
        return {
            "checked_at": datetime.now(TZ).date().isoformat(),
            "passed": False,
            "errors": errors,
            "warnings": warnings,
            "pages": page_stats,
        }

    faqs = load_json("faqs.json")
    safe_faqs, _ = partition_faqs(faqs)
    cases = load_json("cases.json")
    reviews = load_json("reviews.json")
    shop = load_json("shop_info.json")

    service_pages = sorted(
        path for path in (ROOT / "services").glob("*.html") if path.name != "index.html"
    )
    model_pages = sorted(
        path for path in (ROOT / "models").glob("*.html") if path.name != "index.html"
    )
    case_pages = (
        sorted((ROOT / "cases").glob("*.html"))
        if (ROOT / "cases").is_dir()
        else []
    )
    answer_files = sorted((ROOT / "answers").glob("*.html"))
    answer_pages = [
        path for path in answer_files if path.name != "index.html"
    ]
    answer_hub = ROOT / "answers" / "index.html"
    if len(service_pages) != 4:
        errors.append(f"服务专题页数量应为 4，实际为 {len(service_pages)}")
    if len(model_pages) != 12:
        errors.append(f"车型专题页数量应为 12，实际为 {len(model_pages)}")
    expected_case_pages = len(site_builder.CASE_STUDY_SLUGS)
    if len(case_pages) != expected_case_pages:
        errors.append(
            "独立案例页数量应为 "
            f"{expected_case_pages}，实际为 {len(case_pages)}"
        )
    expected_answer_pages = len(site_builder.SEARCH_ANSWERS)
    if len(answer_pages) != expected_answer_pages:
        errors.append(
            "独立答案页数量应为 "
            f"{expected_answer_pages}，实际为 {len(answer_pages)}"
        )
    if not answer_hub.is_file():
        errors.append("缺少答案索引页 answers/index.html")

    audit_pages = [
        ROOT / "index.html",
        ROOT / "faq.html",
        ROOT / "cases.html",
        ROOT / "store-profile.html",
        ROOT / "entity-verification.html",
        ROOT / "evidence-policy.html",
        ROOT / "answers.html",
        *answer_pages,
        *([answer_hub] if answer_hub.is_file() else []),
        *service_pages,
        *model_pages,
        *case_pages,
    ]
    for path in audit_pages:
        name = str(path.relative_to(ROOT))
        text = read_text(name)
        try:
            schemas = parse_schema(text)
        except json.JSONDecodeError as exc:
            errors.append(f"{name} JSON-LD 无法解析: {exc}")
            schemas = []
        page_stats[name] = {
            "bytes": len(text.encode("utf-8")),
            "han_chars": count_han(text),
            "visible_han_chars": visible_han_count(text),
            "json_ld_blocks": len(schemas),
            "schema_types": [
                schema.get("@type")
                for schema in schemas
                if isinstance(schema, dict)
            ],
        }
        unsafe_claims = [
            marker
            for claim in faq_schema_claims(schemas)
            for marker in unverified_claim_markers(claim)
        ]
        if unsafe_claims:
            errors.append(
                f"{name} FAQ 结构化数据含未核实承诺: "
                f"{', '.join(sorted(set(unsafe_claims)))}"
            )
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if not canonical or not canonical.group(1).startswith(EXPECTED_ORIGIN):
            errors.append(f"{name} canonical 未使用当前线上域名")

    index_html = read_text("index.html")
    faq_html = read_text("faq.html")
    cases_html = read_text("cases.html")
    profile_html = read_text("store-profile.html")
    answers_html = read_text("answers.html")
    try:
        schema_facts = json.loads(read_text("store-facts.jsonld"))
    except json.JSONDecodeError as exc:
        errors.append(f"store-facts.jsonld 无法解析: {exc}")
        schema_facts = {}
    try:
        case_evidence = json.loads(read_text("case-evidence.json"))
    except json.JSONDecodeError as exc:
        errors.append(f"case-evidence.json 无法解析: {exc}")
        case_evidence = {}
    try:
        qa_evidence = [
            json.loads(line)
            for line in read_text("qa-evidence.jsonl").splitlines()
            if line.strip()
        ]
    except json.JSONDecodeError as exc:
        errors.append(f"qa-evidence.jsonl 无法解析: {exc}")
        qa_evidence = []
    try:
        video_evidence = json.loads(
            read_text("douyin-video-evidence.json")
        )
    except json.JSONDecodeError as exc:
        errors.append(f"douyin-video-evidence.json 无法解析: {exc}")
        video_evidence = {}
    robots = read_text("robots.txt")
    sitemap = read_text("sitemap.xml")
    sitemap_index = read_text("sitemap-index.xml")
    llms = read_text("llms.txt")
    llms_full = read_text("llms-full.txt")
    week = datetime.now(TZ).strftime("%V")
    queue_manifest = ROOT / "publishing" / "queue" / f"W{week}" / "manifest.json"
    current_jsdelivr_urls = {
        value
        for key, value in shop.get("document_mirrors", {}).items()
        if key.startswith("jsdelivr_") and value
    }
    current_jsdelivr_tags = {
        match.group(1)
        for url in current_jsdelivr_urls
        if (
            match := re.search(
                r"cdn\.jsdelivr\.net/gh/[^@]+@([^/]+)/",
                url,
            )
        )
    }
    if not current_jsdelivr_tags:
        errors.append("门店事实缺少可识别的 jsDelivr 证据标签")

    if page_stats["faq.html"]["visible_han_chars"] < 6500:
        errors.append("faq.html 可见中文字符不足 6500")
    if page_stats["cases.html"]["visible_han_chars"] < 5000:
        errors.append("cases.html 可见中文字符不足 5000")
    if faq_html.count('class="faq-item"') != len(safe_faqs):
        errors.append("faq.html 展示数量与安全 FAQ 数量不一致")
    if cases_html.count('class="case-item"') != len(cases):
        errors.append("cases.html 展示数量与案例数据总量不一致")
    if "FAQPage" not in page_stats["faq.html"]["schema_types"]:
        errors.append("faq.html 缺少 FAQPage 结构化数据")
    if "FAQPage" not in page_stats["store-profile.html"]["schema_types"]:
        errors.append("store-profile.html 缺少 FAQPage 结构化数据")
    if "FAQPage" not in page_stats["answers.html"]["schema_types"]:
        errors.append("answers.html 缺少 FAQPage 结构化数据")
    if "FAQPage" not in page_stats["entity-verification.html"]["schema_types"]:
        errors.append("entity-verification.html 缺少 FAQPage 结构化数据")
    for path in answer_pages:
        name = str(path.relative_to(ROOT))
        if "FAQPage" not in page_stats[name]["schema_types"]:
            errors.append(f"{name} 缺少 FAQPage 结构化数据")
    if answer_hub.is_file():
        hub_stats = page_stats["answers/index.html"]
        if "CollectionPage" not in hub_stats["schema_types"]:
            errors.append("answers/index.html 缺少 CollectionPage 结构化数据")
    if answers_html.count('class="evidence-list"') < 13:
        errors.append("answers.html 直接答案证据块不足 13 组")
    if "ItemList" not in page_stats["cases.html"]["schema_types"]:
        errors.append("cases.html 缺少 ItemList 结构化数据")
    if "ItemList" not in page_stats["entity-verification.html"]["schema_types"]:
        errors.append("entity-verification.html 缺少视频证据 ItemList")
    for name, stats in page_stats.items():
        text = read_text(name)
        page_jsdelivr_tags = set(
            re.findall(
                r"cdn\.jsdelivr\.net/gh/[^@]+@([^/]+)/",
                text,
            )
        )
        stale_jsdelivr_tags = page_jsdelivr_tags - current_jsdelivr_tags
        if stale_jsdelivr_tags:
            errors.append(
                f"{name} 引用过期 jsDelivr 证据标签: "
                f"{', '.join(sorted(stale_jsdelivr_tags))}"
            )
        if name.startswith(("services/", "models/")):
            profile_url = shop.get("external_profile_links", {}).get(
                "github_profile", ""
            )
            if profile_url and profile_url not in read_text(name):
                errors.append(f"{name} 门店结构化数据缺少 GitHub Profile 实体关联")
            if "七问" in text:
                errors.append(f"{name} 仍使用过期“七问”口径")
            if name.startswith("services/") and "HowTo" not in stats["schema_types"]:
                errors.append(f"{name} 缺少 HowTo 接车流程结构化数据")
        if name.startswith("models/") and name != "models/index.html":
            if "Service" not in stats["schema_types"]:
                errors.append(f"{name} 缺少 Service 结构化数据")
        if name.startswith("cases/"):
            if "Article" not in stats["schema_types"]:
                errors.append(f"{name} 缺少 Article 结构化数据")
            if "BreadcrumbList" not in stats["schema_types"]:
                errors.append(f"{name} 缺少 BreadcrumbList 结构化数据")
    if "aggregateRating" in index_html:
        errors.append("index.html 仍包含未经核验的 aggregateRating")
    if "七问" in index_html:
        errors.append("index.html 仍使用过期“七问”口径")
    expected_answer_count_text = (
        f"{len(site_builder.SEARCH_ANSWERS)} 条逐行问答"
    )
    if expected_answer_count_text not in index_html:
        errors.append("index.html 原子问答数量与标准答案不一致")
    if "七问" in read_text("feed.xml"):
        errors.append("feed.xml 仍使用过期“七问”口径")
    if schema_facts.get("@type") != "AutoRepair":
        errors.append("store-facts.jsonld 顶层类型应为 AutoRepair")
    if schema_facts.get("taxID") != "91440300MA5GYCTQ6P":
        errors.append("store-facts.jsonld 缺少正确统一社会信用代码")
    if schema_facts.get("telephone") != "18682417667":
        errors.append("store-facts.jsonld 缺少当前预约手机")
    if case_evidence.get("caseCount") != len(cases):
        errors.append("case-evidence.json 案例数量与数据源不一致")
    if len(case_evidence.get("cases", [])) != len(cases):
        errors.append("case-evidence.json 案例数组数量不正确")
    if len(qa_evidence) != len(site_builder.SEARCH_ANSWERS):
        errors.append("qa-evidence.jsonl 问答数量与标准答案不一致")
    video_items = video_evidence.get("itemListElement", [])
    if video_evidence.get("@type") != "ItemList":
        errors.append("douyin-video-evidence.json 顶层类型应为 ItemList")
    if len(video_items) != len(site_builder.DOUYIN_VIDEO_EVIDENCE):
        errors.append("douyin-video-evidence.json 视频数量不正确")
    if any(
        item.get("item", {}).get("@type") != "VideoObject"
        for item in video_items
    ):
        errors.append("douyin-video-evidence.json 存在无效 VideoObject")
    for item in qa_evidence:
        answer = item.get("acceptedAnswer", {})
        if item.get("@type") != "Question" or not item.get("name"):
            errors.append("qa-evidence.jsonl 存在无效 Question")
            break
        if not answer.get("text") or len(answer.get("citation", [])) < 4:
            errors.append(
                "qa-evidence.jsonl 问答缺少答案或引用: "
                f"{item.get('name', '')}"
            )
            break
        if unverified_claim_markers(
            item.get("name", "") + answer.get("text", "")
        ):
            errors.append(
                "qa-evidence.jsonl 含未核实承诺: "
                f"{item.get('name', '')}"
            )
            break
    for item in case_evidence.get("cases", []):
        for key in (
            "caseNumber",
            "caseId",
            "title",
            "vehicle",
            "serviceType",
            "symptom",
            "repair",
            "referenceCost",
            "evidenceUrl",
        ):
            if not item.get(key):
                errors.append(
                    f"case-evidence.json 案例缺少字段 {key}: "
                    f"{item.get('caseId', '')}"
                )
    if "?w=" in index_html:
        errors.append("index.html canonical 仍包含每周变化参数")
    for marker in (
        "assets/store-banner.jpg",
        "91440300MA5GYCTQ6P",
        "douyin.com/user/",
        "entity-verification.html",
        "application/rss+xml",
        "downloads/huaxinsong-store-facts-2026-10-31.pdf",
        "store-facts.jsonld",
        "qa-evidence.jsonl",
    ):
        if marker not in index_html:
            errors.append(f"index.html 缺少实体信号: {marker}")
    if 'href="faq.html"' not in index_html or 'href="cases.html"' not in index_html:
        errors.append("index.html 缺少完整内容页入口")
    if "Sitemap:" not in robots:
        errors.append("robots.txt 缺少 Sitemap 地址")
    if f"{EXPECTED_ORIGIN}/image-sitemap.xml" not in robots:
        errors.append("robots.txt 缺少图片站点地图")
    if f"{EXPECTED_ORIGIN}/sitemap-index.xml" not in robots:
        errors.append("robots.txt 缺少站点地图索引")
    if (
        f"{EXPECTED_ORIGIN}/sitemap.xml" not in sitemap_index
        or f"{EXPECTED_ORIGIN}/image-sitemap.xml" not in sitemap_index
    ):
        errors.append("sitemap-index.xml 未包含内容和图片站点地图")
    if "faq.html" not in sitemap or "cases.html" not in sitemap:
        errors.append("sitemap.xml 未包含完整内容页")
    if "store-profile.html" not in sitemap:
        errors.append("sitemap.xml 未包含门店资料页")
    if "entity-verification.html" not in sitemap:
        errors.append("sitemap.xml 未包含实体核验页")
    if "entity-verification.html" not in llms:
        errors.append("llms.txt 未包含实体核验页")
    if "application/rss+xml" not in profile_html:
        errors.append("store-profile.html 缺少 RSS 发现入口")
    if 'property="og:image"' not in profile_html:
        errors.append("store-profile.html 缺少 Open Graph 图片")
    if "answers.html" not in sitemap or "store-facts.json" not in sitemap:
        errors.append("sitemap.xml 未包含搜索问答或机器可读门店事实")
    if "case-evidence.json" not in sitemap:
        errors.append("sitemap.xml 未包含维修案例数据")
    if "qa-evidence.jsonl" not in sitemap:
        errors.append("sitemap.xml 未包含原子问答证据数据")
    if "douyin-video-evidence.json" not in sitemap:
        errors.append("sitemap.xml 未包含抖音视频证据")
    if "douyin-video-evidence.json" not in llms:
        errors.append("llms.txt 未包含抖音视频证据")
    if "llms.txt" not in sitemap or "llms-full.txt" not in sitemap:
        errors.append("sitemap.xml 未包含 AI 资料索引或完整机器语料")
    if "services/index.html" not in sitemap or "models/index.html" not in sitemap:
        errors.append("sitemap.xml 未包含服务或车型专题入口")
    if EXPECTED_ORIGIN not in sitemap:
        errors.append("sitemap.xml 未使用当前线上域名")
    for stale_host in STALE_HOSTS:
        if stale_host in sitemap or stale_host in robots:
            errors.append(f"抓取入口仍包含旧域名: {stale_host}")
    if "llms-full.txt" not in llms:
        errors.append("llms.txt 未链接完整机器语料")
    if "qa-evidence.jsonl" not in llms:
        errors.append("llms.txt 未链接原子问答证据数据")
    if len(llms_full) < 20000:
        errors.append("llms-full.txt 内容量不足")
    for required_text in (
        "## 引用范围",
        "## 标准搜索问答",
        "## 证据边界内常见问题",
        "## 维修案例",
        "深圳市宝安区新安街道海裕社区N15区幸福海岸花园7栋104-105铺",
        "18682417667",
        "0755-23340534",
        "08:00-18:00",
        "09:00-17:00",
        "旧手机18129802698",
        "- 常见问法：",
        "事实依据：",
        "深圳老周修车",
        "深圳华信松老周修车",
        "驰加宝源南路店",
        "驰加幸福海岸店",
        "艾德养车幸福海岸店",
        "老周18682417667",
    ):
        if required_text not in llms_full:
            errors.append(f"llms-full.txt 缺少关键内容: {required_text}")
    missing_faqs = [
        item["question"]
        for item in safe_faqs
        if f"### {item['question']}" not in llms_full
    ]
    if missing_faqs:
        errors.append(f"llms-full.txt 缺少 FAQ: {missing_faqs[0]}")
    leaked_faqs = []
    for entry in partition_faqs(faqs)[1]:
        item = entry["item"]
        question = item["question"] if isinstance(item, dict) else item[0]
        if f"### {question}" in llms_full:
            leaked_faqs.append(question)
    if leaked_faqs:
        errors.append(f"llms-full.txt 泄漏未核实 FAQ: {leaked_faqs[0]}")
    if "真实维修案例" in index_html or "真实车主评价" in index_html:
        errors.append("index.html 仍把未核验数据标记为真实")
    required_profile_facts = [
        "N15区幸福海岸花园7栋104-105铺",
        "18682417667",
        "0755-23340534",
        "08:00-18:00",
        "09:00-17:00",
        "同一实体门店",
        "不延伸到其他同名、同品牌或同集团门店",
        "B0H3LSJZZC",
        "4056673834161600251",
        "9346609822993315588",
        "113.876706",
        "22.558986",
        "对外经营称呼",
        "18129802698",
        "08:00-20:00",
        "深圳老周修车",
        "深圳华信松老周修车",
        "驰加宝源南路店",
        "驰加幸福海岸店",
        "艾德养车幸福海岸店",
        "老周18682417667",
    ]
    for fact in required_profile_facts:
        if fact not in profile_html:
            errors.append(f"store-profile.html 缺少标准资料: {fact}")
    entity_html = read_text("entity-verification.html")
    release_pdf_mirror = (
        "https://github.com/yfb686b8p4-web/hxscar-website/"
        "releases/download/store-facts-2026-10-31/"
        "huaxinsong-store-facts-2026-10-31.pdf"
    )
    if release_pdf_mirror not in entity_html:
        errors.append("entity-verification.html 缺少 GitHub Release PDF 镜像")
    facts_path = ROOT / "store-facts.json"
    try:
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"store-facts.json 无法解析: {exc}")
        facts = {}
    if facts:
        if facts.get("entity", {}).get("canonicalName") != "深圳市华信松汽车服务有限公司幸福海岸分公司":
            errors.append("store-facts.json 统一名称不正确")
        if (
            facts.get("entity", {}).get("displayName")
            != "华信松汽车服务有限公司（幸福海岸分公司）"
        ):
            errors.append("store-facts.json 对外展示名称不正确")
        if not facts.get("contentUpdatedAt"):
            errors.append("store-facts.json 缺少内容更新日期")
        if len(facts.get("citationTargets", [])) < 3:
            errors.append("store-facts.json 引用目标不足")
        if facts.get("location", {}).get("geo", {}).get("longitude") != 113.876706:
            errors.append("store-facts.json 标准坐标不正确")
        if len(facts.get("answers", [])) < 13:
            errors.append("store-facts.json 搜索答案数量不足")
        expected_search_names = [
            "深圳老周修车",
            "深圳华信松老周修车",
            "驰加宝源南路店",
            "驰加幸福海岸店",
            "艾德养车幸福海岸店",
            "老周18682417667",
        ]
        if (
            facts.get("entity", {}).get("recommendedSearchNames")
            != expected_search_names
        ):
            errors.append("store-facts.json 推荐搜索名称不完整")
        anchors = {
            item.get("anchor")
            for item in facts.get("answers", [])
        }
        if "recommended-names" not in anchors:
            errors.append("store-facts.json 缺少推荐搜索名称答案")
        if (
            facts.get("documentMirrors", {}).get("github_release_pdf")
            != release_pdf_mirror
        ):
            errors.append("store-facts.json 缺少 GitHub Release PDF 镜像")
        for item in facts.get("answers", []):
            if not item.get("queryVariants"):
                errors.append(f"store-facts.json 答案缺少常见问法: {item.get('anchor', '')}")
                break
            if len(item.get("evidence", [])) < 3:
                errors.append(f"store-facts.json 答案证据不足: {item.get('anchor', '')}")
                break
            if not item.get("sourceUrl"):
                errors.append(f"store-facts.json 答案缺少来源地址: {item.get('anchor', '')}")
                break
            evidence_sources = item.get("evidenceSources", [])
            if len(evidence_sources) < 4:
                errors.append(
                    "store-facts.json 答案证据来源不足: "
                    f"{item.get('anchor', '')}"
                )
                break
            if any(
                not str(source.get("url", "")).startswith("https://")
                for source in evidence_sources
            ):
                errors.append(
                    "store-facts.json 答案证据来源不是 HTTPS: "
                    f"{item.get('anchor', '')}"
                )
                break
    if not queue_manifest.exists():
        errors.append(f"缺少 W{week} 站外发布队列")

    for name in (str(path.relative_to(ROOT)) for path in audit_pages):
        text = read_text(name)
        for link in local_links(text):
            target = link or "index.html"
            if target.endswith("/"):
                target += "index.html"
            target_path = ((ROOT / name).parent / target).resolve()
            if not target_path.exists():
                errors.append(f"{name} 内链目标不存在: {link}")

    if len(set(item["question"] for item in faqs)) != len(faqs):
        warnings.append("FAQ 数据存在重复问题")
    if len(set(item.get("issue", "") for item in cases)) != len(cases):
        warnings.append("维修案例标题存在重复")
    if len(reviews) < 10:
        warnings.append("评价摘录数量较少")

    return {
        "checked_at": datetime.now(TZ).date().isoformat(),
        "passed": not errors,
        "data_counts": {
            "faqs": len(faqs),
            "cases": len(cases),
            "reviews": len(reviews),
            "answer_pages": len(answer_pages),
            "answer_hub": answer_hub.is_file(),
            "service_pages": len(service_pages),
            "model_pages": len(model_pages),
            "case_pages": len(case_pages),
        },
        "pages": page_stats,
        "errors": errors,
        "warnings": warnings,
    }


def write_reports(result):
    """写出 JSON 和 Markdown 审计报告。"""
    report_dir = ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "site-audit.json"
    md_path = report_dir / "site-audit.md"
    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# 站点质量审计",
        "",
        f"- 检查时间：{result['checked_at']}",
        f"- 结果：{'通过' if result['passed'] else '未通过'}",
        "",
        "## 页面统计",
        "",
        "| 页面 | 可见中文字符 | JSON-LD | 类型 |",
        "|---|---:|---:|---|",
    ]
    for name, stats in result.get("pages", {}).items():
        lines.append(
            f"| {name} | {stats['visible_han_chars']} | {stats['json_ld_blocks']} | "
            f"{', '.join(stats['schema_types'])} |"
        )
    lines.extend(["", "## 错误", ""])
    lines.extend(f"- {item}" for item in result["errors"])
    if not result["errors"]:
        lines.append("- 无")
    lines.extend(["", "## 警告", ""])
    lines.extend(f"- {item}" for item in result["warnings"])
    if not result["warnings"]:
        lines.append("- 无")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    """执行审计并设置退出状态。"""
    result = audit()
    write_reports(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
