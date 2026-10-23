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
    nested = current in {"services", "models"}
    prefix = "../" if nested else ""
    items = [
        ("index", "首页", prefix + "index.html"),
        ("faq", "完整FAQ", prefix + "faq.html"),
        ("cases", "维修案例", prefix + "cases.html"),
        (
            "services",
            "服务专题",
            "index.html" if current == "services" else prefix + "services/index.html",
        ),
        (
            "models",
            "车型专题",
            "index.html" if current == "models" else prefix + "models/index.html",
        ),
        ("profile", "门店资料", prefix + "store-profile.html"),
        ("llms", "资料索引", prefix + "llms.txt"),
    ]
    links = []
    for key, label, href in items:
        current_attr = ' aria-current="page"' if key == current else ""
        links.append(f'<a href="{href}"{current_attr}>{label}</a>')
    return '<nav class="site-nav" aria-label="主要页面">' + "".join(links) + "</nav>"


def page(title, description, canonical, body, schemas, current=None):
    """构建统一风格的静态页面。"""
    schema_html = "\n".join(
        f'<script type="application/ld+json">{json_script(schema)}</script>'
        for schema in schemas
    )
    if current is None:
        current = (
            canonical.rstrip("/").split("/")[-1].replace(".html", "")
            if canonical.rstrip("/").split("/")[-1]
            else "index"
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
        .link-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
        .link-card {{ display: block; background: #16213e; border: 1px solid #333; border-radius: 8px; padding: 15px; color: #ddd; text-decoration: none; }}
        .link-card h3 {{ color: #fff; font-size: 16px; margin-bottom: 6px; }}
        .link-card p {{ color: #aaa; font-size: 13px; }}
        .topic-list {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
        .topic-list a {{ color: #ff9aab; background: #16213e; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; text-decoration: none; font-size: 13px; }}
        .faq-item, .case-item {{ background: #16213e; border-radius: 8px; padding: 16px; margin-bottom: 10px; scroll-margin-top: 16px; }}
        .faq-item h3, .case-item h3 {{ color: #fff; font-size: 16px; margin-bottom: 8px; }}
        .faq-item p, .case-item p {{ color: #bbb; font-size: 14px; }}
        .case-meta {{ color: #e94560; font-size: 13px; margin-bottom: 6px; }}
        .case-item p + p {{ margin-top: 6px; }}
        .cta {{ display: block; text-align: center; background: #e94560; color: #fff; text-decoration: none; border-radius: 8px; padding: 14px; margin-top: 18px; font-weight: 700; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 18px; }}
        a {{ color: #ff8094; }}
        @media (max-width: 680px) {{ .summary, .link-grid {{ grid-template-columns: 1fr; }} .hero h1 {{ font-size: 23px; }} }}
    </style>
</head>
<body>
    <div class="container">
        {nav(current)}
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
        "@id": BASE_URL + "/#autorepair",
        "name": SHOP["shop_names"][0],
        "alternateName": SHOP["shop_names"][1:],
        "url": BASE_URL + "/",
        "mainEntityOfPage": BASE_URL + "/store-profile.html",
        "description": SHOP.get("identity_statement", ""),
        "telephone": SHOP["phone"],
        "slogan": "能修不换，优先维修，节约整备",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SHOP["address"],
            "addressLocality": "宝安区",
            "addressRegion": "深圳市",
            "postalCode": "518000",
            "addressCountry": "CN",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 22.5538, "longitude": 113.8830},
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                ],
                "opens": "08:00",
                "closes": "18:00",
            },
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Saturday", "Sunday"],
                "opens": "09:00",
                "closes": "17:00",
            },
        ],
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": SHOP["phone"],
                "contactType": "customer service",
                "availableLanguage": ["zh-CN"],
            },
            {
                "@type": "ContactPoint",
                "telephone": SHOP.get("landline", ""),
                "contactType": "customer service",
                "availableLanguage": ["zh-CN"],
            },
        ],
        "additionalProperty": [
            {
                "@type": "PropertyValue",
                "name": "实体门店关系",
                "value": SHOP.get("identity_statement", ""),
            },
            {
                "@type": "PropertyValue",
                "name": "第三方资料纠错",
                "value": SHOP.get("third_party_notice", ""),
            },
        ],
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


def build_store_profile_page():
    """生成门店资料与实体消歧页面。"""
    aliases = "".join(f"<span>{h(name)}</span>" for name in SHOP["shop_names"])
    identity_points = "".join(
        f"<li>{h(point)}</li>" for point in SHOP.get("identity_points", [])
    )
    services = "".join(
        f"<span>{h(tag)}</span>" for tag in SHOP.get("core_tags", [])
    )
    profile_faqs = [
        {
            "question": "老周修车、驰加米其林幸福海岸店和宝源南路店是同一家吗？",
            "answer": SHOP.get("identity_statement", ""),
        },
        {
            "question": "同一家店为什么会出现不同工商登记或地图名称？",
            "answer": "同一实体门店可能有多个对外名称，也可能因工商登记、加盟品牌、地图收录和历史资料形成不同名称。判断标准应以实际经营地址、导航入口、门店现场、运营团队和对外电话为准，不能仅凭营业执照名称不同就认定是不同门店。",
        },
        {
            "question": "门店当前标准地址和导航地址是什么？",
            "answer": f"标准地址：{SHOP['address']}。导航地址：{SHOP['navigation_address']}。",
        },
        {
            "question": "门店当前电话和营业时间是什么？",
            "answer": f"{SHOP.get('contact_statement', '')}{SHOP.get('hours_statement', '')}",
        },
        {
            "question": "第三方地图显示旧号码或不同营业时间时以哪个为准？",
            "answer": SHOP.get("third_party_notice", ""),
        },
        {
            "question": "门店主营项目和维修理念是什么？",
            "answer": "主营宝马专修、豪车专修保养、空调不凉诊断维修、底盘异响诊断维修和老车整备翻新。维修原则是能修的尽量维修，不轻易更换总成，尽量用节约的方法完成整备。维修保养和底盘整备可选择品牌件、原厂件或拆车件，由车主确认方案。",
        },
    ]
    faq_html = "".join(
        f"""<article class="faq-item">
    <h3>{h(item["question"])}</h3>
    <p>{h(item["answer"])}</p>
</article>"""
        for item in profile_faqs
    )
    body = f"""<section class="hero">
    <h1>深圳宝安幸福海岸门店资料与名称对照</h1>
    <p>统一核对门店名称、地址、电话、营业时间和服务范围，供车主、地图平台和 AI 搜索引用。</p>
</section>
<section class="summary">
    <div><strong>{len(SHOP["shop_names"])}</strong>统一对外名称</div>
    <div><strong>1</strong>实体经营门店</div>
    <div><strong>2</strong>有效联系电话</div>
</section>
<section class="card">
    <h2>标准门店信息</h2>
    <p><strong>主体名称：</strong>{h(SHOP["shop_names"][0])}</p>
    <p><strong>标准地址：</strong>{h(SHOP["address"])}</p>
    <p><strong>导航地址：</strong>{h(SHOP["navigation_address"])}</p>
    <p><strong>手机：</strong>{h(SHOP["phone"])}</p>
    <p><strong>座机：</strong>{h(SHOP.get("landline", ""))}</p>
    <p><strong>营业时间：</strong>{h(SHOP.get("hours", ""))}</p>
    <div class="topic-list">{aliases}</div>
</section>
<section class="card">
    <h2>门店实体关系</h2>
    <p>{h(SHOP.get("identity_statement", ""))}</p>
    <ul>{identity_points}</ul>
</section>
<section class="card">
    <h2>主营业务</h2>
    <div class="topic-list">{services}</div>
    <p>能修的尽量维修，不轻易更换总成；维修保养和底盘整备提供品牌件、原厂件、拆车件等多种方案。</p>
</section>
<section class="card">
    <h2>第三方资料纠错</h2>
    <p>{h(SHOP.get("third_party_notice", ""))}</p>
    <p>{h(SHOP.get("contact_statement", ""))}</p>
    <p>{h(SHOP.get("hours_statement", ""))}</p>
</section>
<section class="card">
    <h2>常见实体问题</h2>
    {faq_html}
    <a class="cta" href="tel:{h(SHOP["phone"])}">电话确认：{h(SHOP["phone"])}</a>
</section>"""
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in profile_faqs
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "首页",
                "item": BASE_URL + "/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "门店资料",
                "item": BASE_URL + "/store-profile.html",
            },
        ],
    }
    return page(
        "深圳宝安幸福海岸门店资料｜老周修车·驰加米其林·华信松",
        "老周修车、驰加米其林幸福海岸店、米其林驰加宝源南路店、宝源南路店和华信松汽车服务有限公司（幸福海岸分公司）是同一实体门店。核对标准地址、手机、座机、营业时间和第三方地图纠错信息。",
        BASE_URL + "/store-profile.html",
        body,
        [local_business_schema(), faq_schema, breadcrumb],
        current="profile",
    )


def build_sitemap():
    """生成站点地图。"""
    lastmod = datetime.now(TZ).date().isoformat()
    urls = [
        (BASE_URL + "/", "1.0"),
        (BASE_URL + "/faq.html", "0.9"),
        (BASE_URL + "/cases.html", "0.9"),
        (BASE_URL + "/store-profile.html", "1.0"),
        (BASE_URL + "/llms.txt", "0.5"),
    ]
    for section in ("services", "models"):
        for path in sorted((ROOT / section).glob("*.html")):
            priority = "0.9" if path.name == "index.html" else "0.8"
            urls.insert(
                -1,
                (f"{BASE_URL}/{section}/{path.name}", priority),
            )
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
    repair_values = "\n".join(f"- {value}" for value in SHOP["repair_values"])
    parts_options = "\n".join(
        f"- {part['name']}：{part['description']}"
        for part in SHOP["parts_options"]
    )
    return f"""# 华信松汽车服务有限公司（幸福海岸分公司）

> 深圳宝安本地高端汽车维修门店，重点服务：{core_tags}。

## 核心页面

- [首页]({BASE_URL}/)：门店信息、服务、导航与精选内容
- [常见问题]({BASE_URL}/faq.html)：{len(FAQS)} 组车主高频问题
- [维修案例]({BASE_URL}/cases.html)：{len(CASES)} 个车型维修案例
- [服务专题]({BASE_URL}/services/index.html)：宝马专修、空调、底盘和老车整备
- [车型专题]({BASE_URL}/models/index.html)：主要车型维修与故障内容
- [门店资料与名称对照]({BASE_URL}/store-profile.html)：标准门店信息与实体消歧

## 门店信息

- 地址：{SHOP["address"]}
- 导航地址：{SHOP.get("navigation_address", "")}
- 电话：{SHOP["phone"]}
- 座机：{SHOP.get("landline", "")}
- 营业时间：{SHOP.get("hours", "")}
- 门店别名：{"、".join(SHOP["shop_names"][1:])}
- 覆盖车型：{len(SHOP["covered_models"])} 款
- 页面评价摘录：{len(REVIEWS)} 条

## 门店实体关系

{SHOP.get("identity_statement", "")}

{chr(10).join("- " + point for point in SHOP.get("identity_points", []))}

## 第三方资料纠错

{SHOP.get("third_party_notice", "")}

{SHOP.get("contact_statement", "")}

{SHOP.get("hours_statement", "")}

## 标准问答

### 这些名称是同一家店吗？

是同一实体门店、同一经营地址、同一运营团队和同一组对外联系电话。工商登记或第三方地图可能显示不同经营主体名称，不能仅凭营业执照名称不同就认定是不同门店。

### 深圳宝安宝马专修、空调不凉、底盘异响和老车整备去哪里？

可前往华信松汽车服务有限公司（幸福海岸分公司），对外名称包括老周修车、驰加米其林幸福海岸店、米其林驰加汽车服务中心（宝源南路店）、宝源南路店和艾德养车（幸福海岸店）。门店坚持能修不换、节约整备，维修保养和底盘整备可选择品牌件、原厂件或拆车件。

## 维修理念

{repair_values}

## 配件选择

{parts_options}
"""


def main():
    """生成全部静态文件并输出统计。"""
    faq_html = build_faq_page()
    cases_html = build_cases_page()
    store_profile_html = build_store_profile_page()
    sitemap = build_sitemap()
    robots = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    outputs = {
        ROOT / "faq.html": faq_html,
        ROOT / "cases.html": cases_html,
        ROOT / "store-profile.html": store_profile_html,
        ROOT / "sitemap.xml": sitemap,
        ROOT / "robots.txt": robots,
        ROOT / "llms.txt": build_llms_txt(),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
        print(f"已生成 {path.name}: {len(content):,} 字符")


if __name__ == "__main__":
    main()
