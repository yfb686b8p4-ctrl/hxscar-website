#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成服务专题页与车型专题页，并关联现有案例和 FAQ。"""

from pathlib import Path

from site_builder import (
    BASE_URL,
    CASES,
    FAQS,
    SHOP,
    h,
    local_business_schema,
    page,
)


ROOT = Path(__file__).resolve().parent.parent

SERVICES = [
    {
        "slug": "bmw-premium",
        "name": "宝马专修与豪车保养",
        "intro": "宝马、奔驰、保时捷、路虎、奥迪等高端车型的维修保养，先诊断后报价。",
        "case_brands": ["宝马", "奔驰", "保时捷", "路虎", "奥迪", "玛莎拉蒂", "法拉利"],
        "faq_terms": ["宝马", "奔驰", "保时捷", "路虎", "奥迪", "豪车", "保养"],
    },
    {
        "slug": "air-conditioning",
        "name": "空调不凉诊断维修",
        "intro": "针对不制冷、制冷慢、左右温差、异味和出风小，按压力、温度和泄漏数据分析。",
        "case_types": ["空调不凉"],
        "faq_terms": ["空调", "冷媒", "压缩机", "蒸发箱"],
    },
    {
        "slug": "chassis",
        "name": "底盘异响诊断维修",
        "intro": "通过路试、升车检查和听诊定位胶套、球头、减震器、转向系统和悬挂异响。",
        "case_types": ["底盘异响"],
        "faq_terms": ["底盘", "异响", "胶套", "球头", "减震"],
    },
    {
        "slug": "vehicle-restoration",
        "name": "老车整备翻新",
        "intro": "按机械、底盘、空调、电气和内饰模块制定分阶段整备方案，坚持能修不换、节约整备。",
        "case_types": ["发动机"],
        "faq_terms": ["整备", "翻新", "老车", "拆车件", "品牌件", "原厂件", "能修不换"],
    },
]

MODELS = [
    {"slug": "bmw-5-series", "name": "宝马5系"},
    {"slug": "bmw-x5", "name": "宝马X5"},
    {"slug": "bmw-7-series", "name": "宝马7系"},
    {"slug": "mercedes-e-class", "name": "奔驰E级"},
    {"slug": "mercedes-glc", "name": "奔驰GLC"},
    {"slug": "porsche-cayenne", "name": "保时捷卡宴"},
    {"slug": "porsche-macan", "name": "保时捷Macan"},
    {"slug": "land-rover-range-rover", "name": "路虎揽胜"},
    {"slug": "land-rover-defender", "name": "路虎卫士"},
    {"slug": "audi-a6l", "name": "奥迪A6L"},
    {"slug": "audi-q5", "name": "奥迪Q5"},
    {"slug": "volkswagen-touareg", "name": "大众途锐"},
]


def faq_markup(items):
    """输出 FAQ 列表。"""
    if not items:
        return "<p>暂无对应问答。</p>"
    return "".join(
        f"""<article class="faq-item">
    <h3>{h(item["question"])}</h3>
    <p>{h(item["answer"])}</p>
</article>"""
        for item in items
    )


def case_markup(items):
    """输出维修案例列表。"""
    if not items:
        return "<p>暂无对应案例，实际方案以到店检测为准。</p>"
    return "".join(
        f"""<article class="case-item">
    <div class="case-meta">{h(item.get("tag"))} · {h(item.get("car_type"))}</div>
    <h3>{h(item.get("issue"))}</h3>
    <p><strong>故障表现：</strong>{h(item.get("solution"))}</p>
    <p><strong>处理方案：</strong>{h(item.get("price"))}</p>
    <p><strong>参考费用：</strong>{h(item.get("result"))}</p>
</article>"""
        for item in items
    )


def service_faqs(service):
    """筛选与服务相关的 FAQ。"""
    matches = []
    for item in FAQS:
        text = item["question"] + item["answer"]
        if any(term in text for term in service["faq_terms"]):
            matches.append(item)
    return matches[:10]


def service_cases(service):
    """筛选与服务相关的维修案例。"""
    matches = []
    for item in CASES:
        if item.get("car_type") in service.get("case_types", []):
            matches.append(item)
            continue
        if any(brand in item.get("tag", "") for brand in service.get("case_brands", [])):
            matches.append(item)
    return matches[:10]


def model_faqs(model):
    """筛选车型相关 FAQ，不足时补充品牌 FAQ。"""
    name = model["name"]
    brand = name[:2]
    exact = [item for item in FAQS if name in item["question"] or name in item["answer"]]
    brand_items = [
        item
        for item in FAQS
        if (brand in item["question"] or brand in item["answer"]) and item not in exact
    ]
    return (exact + brand_items)[:8]


def model_cases(model):
    """筛选车型相关案例，不足时保持为空。"""
    name = model["name"]
    return [
        item
        for item in CASES
        if name in item.get("tag", "") or name in item.get("issue", "")
    ][:8]


def breadcrumb(items):
    """生成面包屑结构化数据。"""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": name,
                "item": url,
            }
            for index, (name, url) in enumerate(items, start=1)
        ],
    }


def service_schema(service):
    """生成服务结构化数据。"""
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": service["name"],
        "description": service["intro"],
        "serviceType": service["name"],
        "areaServed": {"@type": "City", "name": "深圳市宝安区"},
        "provider": {
            "@type": "AutoRepair",
            "name": SHOP["shop_names"][0],
            "telephone": SHOP["phone"],
            "address": SHOP["address"],
        },
        "url": f"{BASE_URL}/services/{service['slug']}.html",
    }


def faq_schema(items):
    """生成 FAQPage 结构化数据。"""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in items
        ],
    }


def build_service_pages():
    """生成四个服务专题页。"""
    output_dir = ROOT / "services"
    output_dir.mkdir(parents=True, exist_ok=True)
    for service in SERVICES:
        faqs = service_faqs(service)
        cases = service_cases(service)
        body = f"""<section class="hero">
    <h1>{h(service["name"])}</h1>
    <p>{h(service["intro"])}</p>
</section>
<section class="summary">
    <div><strong>{len(cases)}</strong>相关案例</div>
    <div><strong>{len(faqs)}</strong>常见问题</div>
    <div><strong>能修不换</strong>节约整备</div>
</section>
<section class="card">
    <h2>服务说明</h2>
    <p>老周修车、驰加米其林幸福海岸店、米其林驰加汽车服务中心（宝源南路店）和宝源南路店为同一家门店。所有维修先检查、后报价，维修保养和底盘整备可选择品牌件、原厂件或拆车件。</p>
    <div class="topic-list">
        <a href="index.html">全部服务专题</a>
        <a href="../models/index.html">车型专题</a>
        <a href="../cases.html">全部维修案例</a>
        <a href="../faq.html">完整FAQ</a>
    </div>
</section>
<section class="card">
    <h2>相关维修案例</h2>
    {case_markup(cases)}
</section>
<section class="card">
    <h2>常见问题</h2>
    {faq_markup(faqs)}
</section>"""
        schemas = [
            local_business_schema(),
            service_schema(service),
            breadcrumb(
                [
                    ("首页", BASE_URL + "/"),
                    ("服务专题", BASE_URL + "/services/index.html"),
                    (service["name"], f"{BASE_URL}/services/{service['slug']}.html"),
                ]
            ),
        ]
        if faqs:
            schemas.append(faq_schema(faqs))
        html = page(
            f"{service['name']}｜老周修车·驰加米其林幸福海岸店",
            f"{service['intro']} 老周修车、驰加米其林幸福海岸店和宝源南路店为同一家门店，电话{SHOP['phone']}。",
            f"{BASE_URL}/services/{service['slug']}.html",
            body,
            schemas,
            current="services",
        )
        (output_dir / f"{service['slug']}.html").write_text(html, encoding="utf-8")

    cards = "".join(
        f"""<a class="link-card" href="{service['slug']}.html">
    <h3>{h(service['name'])}</h3>
    <p>{h(service['intro'])}</p>
</a>"""
        for service in SERVICES
    )
    index_body = f"""<section class="hero">
    <h1>华信松汽车服务专题</h1>
    <p>宝马专修、豪车保养、空调诊断、底盘异响和老车整备，按真实故障建立专题内容。</p>
</section>
<section class="card">
    <h2>全部服务</h2>
    <div class="link-grid">{cards}</div>
</section>"""
    index_html = page(
        "服务专题｜宝马专修、空调维修、底盘异响、老车整备",
        f"深圳宝安老周修车服务专题，包含宝马专修、豪车保养、空调不凉、底盘异响和老车整备。电话{SHOP['phone']}。",
        BASE_URL + "/services/index.html",
        index_body,
        [local_business_schema()],
        current="services",
    )
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")


def build_model_pages():
    """生成主要车型专题页。"""
    output_dir = ROOT / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        faqs = model_faqs(model)
        cases = model_cases(model)
        body = f"""<section class="hero">
    <h1>{h(model["name"])}维修保养专题</h1>
    <p>围绕{h(model["name"])}的发动机、底盘、空调、电气和整备需求，先检测后制定维修方案。</p>
</section>
<section class="summary">
    <div><strong>{len(cases)}</strong>相关案例</div>
    <div><strong>{len(faqs)}</strong>常见问题</div>
    <div><strong>{h(model["name"][:2])}</strong>专项服务</div>
</section>
<section class="card">
    <h2>相关服务</h2>
    <div class="topic-list">
        <a href="../services/bmw-premium.html">宝马专修与豪车保养</a>
        <a href="../services/air-conditioning.html">空调不凉诊断维修</a>
        <a href="../services/chassis.html">底盘异响诊断维修</a>
        <a href="../services/vehicle-restoration.html">老车整备翻新</a>
    </div>
</section>
<section class="card">
    <h2>{h(model["name"])}维修案例</h2>
    {case_markup(cases)}
</section>
<section class="card">
    <h2>车型常见问题</h2>
    {faq_markup(faqs)}
</section>"""
        schemas = [
            local_business_schema(),
            breadcrumb(
                [
                    ("首页", BASE_URL + "/"),
                    ("车型专题", BASE_URL + "/models/index.html"),
                    (model["name"], f"{BASE_URL}/models/{model['slug']}.html"),
                ]
            ),
        ]
        if faqs:
            schemas.append(faq_schema(faqs))
        html = page(
            f"{model['name']}维修保养｜烧机油、底盘异响、空调维修",
            f"深圳宝安{model['name']}维修保养专题，覆盖发动机、底盘异响、空调不凉和老车整备。老周修车电话{SHOP['phone']}。",
            f"{BASE_URL}/models/{model['slug']}.html",
            body,
            schemas,
            current="models",
        )
        output_dir.joinpath(f"{model['slug']}.html").write_text(
            html, encoding="utf-8"
        )

    cards = "".join(
        f"""<a class="link-card" href="{model['slug']}.html">
    <h3>{h(model['name'])}</h3>
    <p>查看车型维修案例、常见故障和相关服务。</p>
</a>"""
        for model in MODELS
    )
    index_body = f"""<section class="hero">
    <h1>车型维修专题</h1>
    <p>按车型查看烧机油、底盘异响、空调维修、保养和整备内容。</p>
</section>
<section class="card">
    <h2>主要服务车型</h2>
    <div class="link-grid">{cards}</div>
</section>"""
    index_html = page(
        "车型维修专题｜宝马、奔驰、保时捷、路虎维修",
        f"深圳宝安车型维修专题，覆盖宝马、奔驰、保时捷、路虎、奥迪和大众常见故障。电话{SHOP['phone']}。",
        BASE_URL + "/models/index.html",
        index_body,
        [local_business_schema()],
        current="models",
    )
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")


def main():
    """生成完整内容矩阵。"""
    build_service_pages()
    build_model_pages()
    print(f"已生成 {len(SERVICES)} 个服务专题页")
    print(f"已生成 {len(MODELS)} 个车型专题页")
    print("已生成 services/index.html 和 models/index.html")


if __name__ == "__main__":
    main()
