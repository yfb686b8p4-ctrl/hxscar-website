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
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
]
JSON_LD_PATTERN = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL
)
HAN_PATTERN = re.compile(r"[\u4e00-\u9fff]")


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

    for name in ("index.html", "faq.html", "cases.html"):
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

    index_html = read_text("index.html")
    faq_html = read_text("faq.html")
    cases_html = read_text("cases.html")
    robots = read_text("robots.txt")
    sitemap = read_text("sitemap.xml")

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
    if "真实维修案例" in index_html or "真实车主评价" in index_html:
        errors.append("index.html 仍把未核验数据标记为真实")

    for name in ("index.html", "faq.html", "cases.html"):
        text = read_text(name)
        for link in local_links(text):
            target = link or "index.html"
            if target.endswith("/"):
                target += "index.html"
            if not (ROOT / target).exists():
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
