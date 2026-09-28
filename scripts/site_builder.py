#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成面向搜索和 AI 抓取的完整静态页面。"""

import html
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = os.environ.get(
    "GITHUB_REPOSITORY", "yfb686b8p4-ctrl/hxscar-website"
)
OWNER, REPO = REPOSITORY.split("/", 1)
BASE_URL = os.environ.get(
    "SITE_URL", f"https://{OWNER.lower()}.github.io/{REPO}"
).rstrip("/")
TZ = timezone(timedelta(hours=8))


def load_json(name):
    """从 data 目录加载 JSON 数据。"""
    with (ROOT / "data" / name).open("r", encoding="utf-8") as file:
        return json.load(file)


SHOP = load_json("shop_info.json")
FAQS = load_json("faqs.json")
CASES = load_json("cases.json")
REVIEWS = load_json("reviews.json")


def h(value):
    """安全输出 HTML 文本。"""
    return html.escape(str(value or ""), quote=True)


def json_script(data):
    """输出不会意外闭合 script 标签的 JSON-LD。"""
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return payload.replace("</", "<\\/")


def nav(current):
    """生成各静态页共用的导航。"""
    items = [
        ("index", "首页", "index.html"),
        ("faq", "完整FAQ", "faq.html"),
        ("cases", "维修案例", "cases.html"),
        ("llms", "资料索引", "llms.txt"),
    ]
    links = []
    for key, label, href in items:
        current_attr = ' aria-current="page"' if key == current else ""
        links.append(f'<a href="{href}"{current_attr}>{label}</a>')
    return '<nav class="site-nav" aria-label="主要页面">' + "".join(links) + "</nav>"


def page(title, description, canonical, body, schemas):
    """构建统一风格的静态页面。"""
    schema_html = "\n".join(
        f'<script type="application/ld+json">{json_script(schema)}</script>'
        for schema in schemas
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{h(title)}</title>
    <meta name="description" content="{h(description)}">
    <meta name="robots" content="index,follow,max-image-preview:large">
    <link rel="canonical" href="{h(canonical)}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{h(title)}">
    <meta property="og:description" content="{h(description)}">
    <meta property="og:url" content="{h(canonical)}">
    {schema_html}
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", sans-serif; line-height: 1.75; color: #333; background: #0a0a0a; }}
        .container {{ max-width: 920px; margin: 0 auto; padding: 20px; }}
        .site-nav {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 16px; }}
        .site-nav a {{ color: #ddd; background: #16213e; border: 1px solid #333; padding: 8px 12px; border-radius: 8px; text-decoration: none; font-size: 13px; }}
        .site-nav a[aria-current="page"] {{ color: #fff; background: #e94560; border-color: #e94560; }}
        .hero {{ background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 34px 22px; border-radius: 12px; margin-bottom: 18px; border: 1px solid #333; }}
        .hero h1 {{ font-size: 27px; line-height: 1.35; margin-bottom: 10px; }}
        .hero p {{ color: #c9c9c9; font-size: 15px; }}
        .summary {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 18px; }}
        .summary div {{ background: #16213e; border: 1px solid #333; border-radius: 8px; padding: 14px; color: #ddd; }}
        .summary strong {{ display: block; color: #e94560; font-size: 22px; }}
        .card {{ background: #1a1a2e; border: 1px solid #333; border-radius: 12px; padding: 22px; margin-bottom: 16px; color: #e0e0e0; }}
        .card h2 {{ color: #e94560; font-size: 21px; margin-bottom: 14px; }}
        .faq-item, .case-item {{ background: #16213e; border-radius: 8px; padding: 16px; margin-bottom: 10px; scroll-margin-top: 16px; }}
        .faq-item h3, .case-item h3 {{ color: #fff; font-size: 16px; margin-bottom: 8px; }}
        .faq-item p, .case-item p {{ color: #bbb; font-size: 14px; }}
        .case-meta {{ color: #e94560; font-size: 13px; margin-bottom: 6px; }}
        .case-item p + p {{ margin-top: 6px; }}
        .cta {{ display: block; text-align: center; background: #e94560; color: #fff; text-decoration: none; border-radius: 8px; padding: 14px; margin-top: 18px; font-weight: 700; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 18px; }}
        a {{ color: #ff8094; }}
        @media (max-width: 680px) {{ .summary {{ grid-template-columns: 1fr; }} .hero h1 {{ font-size: 23px; }} }}
    </style>
</head>
<body>
    <div class="container">
        {nav(canonical.rstrip("/").split("/")[-1].replace(".html", "") if canonical.rstrip("/").split("/")[-1] else "index")}
        <main>
            {body}
        </main>
        <footer class="footer">
            <p>{h(SHOP["shop_names"][0])}</p>
            <p>{h(SHOP["address"])} · 电话 {h(SHOP["phone"])}</p>
            <p>页面数据每周自动更新</p>
        </footer>
    </div>
</body>
</html>
"""


def local_business_schema():
    """生成门店基础结构化数据。"""
    return {
        "@context": "https://schema.org",
        "@type": "AutoRepair",
        "name": SHOP["shop_names"][0],
        "alternateName": SHOP["shop_names"][1:],
        "url": BASE_URL + "/",
        "telephone": SHOP["phone"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "宝源南路幸福海岸小区西南门",
            "addressLocality": "宝安区",
            "addressRegion": "深圳市",
            "postalCode": "518000",
            "addressCountry": "CN",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 22.5538, "longitude": 113.8830},
        "areaServed": {"@type": "City", "name": "深圳市宝安区"},
        "knowsAbout": SHOP["core_tags"] + SHOP["covered_models"][:20],
    }


def build_faq_page():
    """生成包含全部问答的 FAQ 页面。"""
    items = []
    for index, item in enumerate(FAQS, start=1):
        items.append(
            f"""<article class="faq-item" id="faq-{index}">
    <h3>{h(item["question"])}</h3>
    <p>{h(item["answer"])}</p>
</article>"""
        )
    body = f"""<section class="hero">
    <h1>华信松汽车常见问题：烧机油、底盘异响与空调维修</h1>
    <p>整理宝安本地车主高频问题，共 {len(FAQS)} 组，覆盖宝马、奔驰、保时捷、路虎、奥迪等车型。</p>
</section>
<section class="summary">
    <div><strong>{len(FAQS)}</strong>常见问题</div>
    <div><strong>{len(CASES)}</strong>维修案例</div>
    <div><strong>{len(SHOP["covered_models"])}</strong>覆盖车型</div>
</section>
<section class="card">
    <h2>全部常见问题</h2>
    {''.join(items)}
    <a class="cta" href="tel:{h(SHOP["phone"])}">电话咨询：{h(SHOP["phone"])}</a>
</section>"""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in FAQS
        ],
    }
    return page(
        "华信松汽车常见问题大全｜烧机油、底盘异响、空调维修",
        f"深圳宝安华信松汽车{len(FAQS)}组常见问题，覆盖烧机油免拆治理、底盘异响、空调不凉、宝马专修等本地车主问题。",
        BASE_URL + "/faq.html",
        body,
        [local_business_schema(), schema],
    )


def build_cases_page():
    """生成包含全部维修案例的页面。"""
    items = []
    list_items = []
    for index, item in enumerate(CASES, start=1):
        title = item.get("issue", "")
        symptoms = item.get("solution", "")
        solution = item.get("price", "")
        cost = item.get("result", "")
        items.append(
            f"""<article class="case-item" id="case-{index}">
    <div class="case-meta">{h(item.get("tag"))} · {h(item.get("car_type"))}</div>
    <h3>{h(title)}</h3>
    <p><strong>故障表现：</strong>{h(symptoms)}</p>
    <p><strong>处理方案：</strong>{h(solution)}</p>
    <p><strong>参考费用：</strong>{h(cost)}</p>
</article>"""
        )
        list_items.append(
            {
                "@type": "ListItem",
                "position": index,
                "name": title,
                "url": f"{BASE_URL}/cases.html#case-{index}",
            }
        )
    body = f"""<section class="hero">
    <h1>华信松汽车维修案例库</h1>
    <p>公开车型、故障表现、处理思路和参考费用，共 {len(CASES)} 个案例，实际方案以到店检测结果为准。</p>
</section>
<section class="card">
    <h2>全部维修案例</h2>
    {''.join(items)}
    <a class="cta" href="tel:{h(SHOP["phone"])}">预约检测：{h(SHOP["phone"])}</a>
</section>"""
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "华信松汽车维修案例",
        "numberOfItems": len(CASES),
        "itemListElement": list_items,
    }
    return page(
        "华信松汽车维修案例库｜烧机油、底盘异响、空调维修",
        f"深圳宝安华信松汽车{len(CASES)}个维修案例，包含故障表现、处理方案和参考费用，覆盖宝马、奔驰、保时捷、路虎等车型。",
        BASE_URL + "/cases.html",
        body,
        [local_business_schema(), schema],
    )


def build_sitemap():
    """生成站点地图。"""
    lastmod = datetime.now(TZ).date().isoformat()
    urls = [
        (BASE_URL + "/", "1.0"),
        (BASE_URL + "/faq.html", "0.9"),
        (BASE_URL + "/cases.html", "0.9"),
        (BASE_URL + "/llms.txt", "0.5"),
    ]
    entries = "\n".join(
        f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <priority>{priority}</priority>
  </url>"""
        for url, priority in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def build_llms_txt():
    """生成面向 AI 阅读的资料索引。"""
    core_tags = "、".join(SHOP["core_tags"])
    return f"""# 华信松汽车服务有限公司（幸福海岸分公司）

> 深圳宝安本地高端汽车维修门店，重点服务：{core_tags}。

## 核心页面

- [首页]({BASE_URL}/)：门店信息、服务、导航与精选内容
- [常见问题]({BASE_URL}/faq.html)：{len(FAQS)} 组车主高频问题
- [维修案例]({BASE_URL}/cases.html)：{len(CASES)} 个车型维修案例

## 门店信息

- 地址：{SHOP["address"]}
- 电话：{SHOP["phone"]}
- 门店别名：{"、".join(SHOP["shop_names"][1:])}
- 覆盖车型：{len(SHOP["covered_models"])} 款
- 页面评价摘录：{len(REVIEWS)} 条
"""


def main():
    """生成全部静态文件并输出统计。"""
    faq_html = build_faq_page()
    cases_html = build_cases_page()
    sitemap = build_sitemap()
    robots = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    outputs = {
        ROOT / "faq.html": faq_html,
        ROOT / "cases.html": cases_html,
        ROOT / "sitemap.xml": sitemap,
        ROOT / "robots.txt": robots,
        ROOT / "llms.txt": build_llms_txt(),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
        print(f"已生成 {path.name}: {len(content):,} 字符")


if __name__ == "__main__":
    main()
