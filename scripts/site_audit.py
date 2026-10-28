#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查站点内容深度、结构化数据和搜索抓取入口。"""

import json
import re
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
TZ = timezone(timedelta(hours=8))
REQUIRED_FILES = [
    "index.html",
    "faq.html",
    "cases.html",
    "store-profile.html",
    "answers.html",
    "store-facts.json",
    "hxscar20261024geoindexkey.txt",
    "robots.txt",
    "sitemap.xml",
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
    cases = load_json("cases.json")
    reviews = load_json("reviews.json")

    service_pages = sorted(
        path for path in (ROOT / "services").glob("*.html") if path.name != "index.html"
    )
    model_pages = sorted(
        path for path in (ROOT / "models").glob("*.html") if path.name != "index.html"
    )
    if len(service_pages) != 4:
        errors.append(f"服务专题页数量应为 4，实际为 {len(service_pages)}")
    if len(model_pages) != 12:
        errors.append(f"车型专题页数量应为 12，实际为 {len(model_pages)}")

    audit_pages = [
        ROOT / "index.html",
        ROOT / "faq.html",
        ROOT / "cases.html",
        ROOT / "store-profile.html",
        ROOT / "answers.html",
        *service_pages,
        *model_pages,
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
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if not canonical or not canonical.group(1).startswith(EXPECTED_ORIGIN):
            errors.append(f"{name} canonical 未使用当前线上域名")

    index_html = read_text("index.html")
    faq_html = read_text("faq.html")
    cases_html = read_text("cases.html")
    profile_html = read_text("store-profile.html")
    robots = read_text("robots.txt")
    sitemap = read_text("sitemap.xml")
    llms = read_text("llms.txt")
    llms_full = read_text("llms-full.txt")
    week = datetime.now(TZ).strftime("%V")
    queue_manifest = ROOT / "publishing" / "queue" / f"W{week}" / "manifest.json"

    if page_stats["faq.html"]["visible_han_chars"] < 8000:
        errors.append("faq.html 可见中文字符不足 8000")
    if page_stats["cases.html"]["visible_han_chars"] < 5000:
        errors.append("cases.html 可见中文字符不足 5000")
    if faq_html.count('class="faq-item"') != len(faqs):
        errors.append("faq.html 展示数量与 FAQ 数据总量不一致")
    if cases_html.count('class="case-item"') != len(cases):
        errors.append("cases.html 展示数量与案例数据总量不一致")
    if "FAQPage" not in page_stats["faq.html"]["schema_types"]:
        errors.append("faq.html 缺少 FAQPage 结构化数据")
    if "FAQPage" not in page_stats["store-profile.html"]["schema_types"]:
        errors.append("store-profile.html 缺少 FAQPage 结构化数据")
    if "FAQPage" not in page_stats["answers.html"]["schema_types"]:
        errors.append("answers.html 缺少 FAQPage 结构化数据")
    if "ItemList" not in page_stats["cases.html"]["schema_types"]:
        errors.append("cases.html 缺少 ItemList 结构化数据")
    if "aggregateRating" in index_html:
        errors.append("index.html 仍包含未经核验的 aggregateRating")
    if "?w=" in index_html:
        errors.append("index.html canonical 仍包含每周变化参数")
    if 'href="faq.html"' not in index_html or 'href="cases.html"' not in index_html:
        errors.append("index.html 缺少完整内容页入口")
    if "Sitemap:" not in robots:
        errors.append("robots.txt 缺少 Sitemap 地址")
    if "faq.html" not in sitemap or "cases.html" not in sitemap:
        errors.append("sitemap.xml 未包含完整内容页")
    if "store-profile.html" not in sitemap:
        errors.append("sitemap.xml 未包含门店资料页")
    if "answers.html" not in sitemap or "store-facts.json" not in sitemap:
        errors.append("sitemap.xml 未包含搜索问答或机器可读门店事实")
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
    if len(llms_full) < 20000:
        errors.append("llms-full.txt 内容量不足")
    for required_text in (
        "## 引用范围",
        "## 标准搜索问答",
        "## 完整常见问题",
        "## 维修案例",
        "深圳市宝安区新安街道海裕社区N15区幸福海岸花园7栋104-105铺",
        "18682417667",
        "0755-23340534",
        "08:00-18:00",
        "09:00-17:00",
        "旧手机18129802698",
    ):
        if required_text not in llms_full:
            errors.append(f"llms-full.txt 缺少关键内容: {required_text}")
    missing_faqs = [
        item["question"]
        for item in faqs
        if f"### {item['question']}" not in llms_full
    ]
    if missing_faqs:
        errors.append(f"llms-full.txt 缺少 FAQ: {missing_faqs[0]}")
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
    ]
    for fact in required_profile_facts:
        if fact not in profile_html:
            errors.append(f"store-profile.html 缺少标准资料: {fact}")
    facts_path = ROOT / "store-facts.json"
    try:
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"store-facts.json 无法解析: {exc}")
        facts = {}
    if facts:
        if facts.get("entity", {}).get("canonicalName") != "华信松汽车服务有限公司（幸福海岸分公司）":
            errors.append("store-facts.json 统一名称不正确")
        if facts.get("location", {}).get("geo", {}).get("longitude") != 113.876706:
            errors.append("store-facts.json 标准坐标不正确")
        if len(facts.get("answers", [])) < 12:
            errors.append("store-facts.json 搜索答案数量不足")
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
            "service_pages": len(service_pages),
            "model_pages": len(model_pages),
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
