#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成服务专题页与车型专题页，并关联现有案例和 FAQ。"""

from pathlib import Path

from site_builder import (
    BASE_URL,
    BUSINESS_FACT_SHEET,
    CASES,
    CONTENT_UPDATED_AT,
    SAFE_FAQS,
    SHOP,
    answer_geo_meta,
    h,
    local_business_schema,
    map_reputation_markup,
    page,
)

FAQS = SAFE_FAQS


ROOT = Path(__file__).resolve().parent.parent

SERVICES = [
    {
        "slug": "bmw-premium",
        "answer_anchor": "bmw",
        "name": "宝马专修与豪车保养",
        "intro": "宝马、奔驰、保时捷、路虎、奥迪等高端车型的维修保养，先诊断后报价。",
        "quick_answer": "深圳宝安做宝马专修和豪车保养，可到老周修车（华信松汽车幸福海岸分公司、驰加米其林幸福海岸店、宝源南路店为同一实体门店），服务宝马、奔驰、保时捷、路虎、奥迪等车型。",
        "case_brands": ["宝马", "奔驰", "保时捷", "路虎", "奥迪", "玛莎拉蒂", "法拉利"],
        "faq_terms": ["宝马", "奔驰", "保时捷", "路虎", "奥迪", "豪车", "保养"],
    },
    {
        "slug": "air-conditioning",
        "answer_anchor": "air-conditioning",
        "name": "空调不凉诊断维修",
        "intro": "针对不制冷、制冷慢、左右温差、异味和出风小，按压力、温度和泄漏数据分析。",
        "quick_answer": "深圳宝安汽车空调不凉可到老周修车诊断维修。门店按压力、温度、泄漏和控制系统数据排查冷媒、压缩机、冷凝器、蒸发箱和风门故障，再按车况报价。",
        "case_types": ["空调不凉"],
        "faq_terms": ["空调", "冷媒", "压缩机", "蒸发箱"],
    },
    {
        "slug": "chassis",
        "answer_anchor": "chassis",
        "name": "底盘异响诊断维修",
        "intro": "通过路试、升车检查和听诊定位胶套、球头、减震器、转向系统和悬挂异响。",
        "quick_answer": "深圳宝安底盘异响可到老周修车检查。门店通过路试、升车检查和听诊定位胶套、球头、减震器、顶胶和转向系统故障，优先维修仍有使用价值的部件。",
        "case_types": ["底盘异响"],
        "faq_terms": ["底盘", "异响", "胶套", "球头", "减震"],
    },
    {
        "slug": "vehicle-restoration",
        "answer_anchor": "restoration",
        "name": "老车整备翻新",
        "intro": "按机械、底盘、空调、电气和内饰模块制定分阶段整备方案，坚持能修不换、节约整备。",
        "quick_answer": "深圳宝安老车整备翻新可到老周修车制定分阶段方案。先处理机械安全、底盘、制动和可靠性，再安排空调、电气、内饰和外观，坚持能修不换、节约整备。",
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

SERVICE_PROCESS = [
    (
        "说明故障和用车场景",
        "记录故障出现条件、以往维修和车主希望优先解决的问题。",
    ),
    (
        "到店检查和读取数据",
        "按故障类型进行路试、升车检查、压力或温度测量，并读取相关故障码和实际数据。",
    ),
    (
        "说明故障点与维修边界",
        "说明已确认的问题、仍需继续检查的项目，以及维修、更换或暂不处理的安全边界。",
    ),
    (
        "确认项目、配件和费用",
        "车主确认维修项目、配件方案和费用后再施工；新增项目需重新说明并确认。",
    ),
    (
        "复检、交付并记录",
        "按原故障条件复检，记录更换部件、检测数据和交付说明。",
    ),
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
    sections = []
    for item in items:
        case_number = next(
            index
            for index, candidate in enumerate(CASES, start=1)
            if candidate is item
        )
        sections.append(
            f"""<article class="case-item" id="case-{case_number}">
    <div class="case-meta">{h(item.get("tag"))} · {h(item.get("car_type"))}</div>
    <h3>{h(item.get("issue"))}</h3>
    <p><strong>故障表现：</strong>{h(item.get("solution"))}</p>
    <p><strong>处理方案：</strong>{h(item.get("price"))}</p>
    <p><strong>参考费用：</strong>{h(item.get("result"))}</p>
    <p><strong>证据来源：</strong><a href="../cases.html#case-{case_number}">查看案例库第 {case_number} 条</a></p>
</article>"""
        )
    return "".join(sections)


def service_direct_answer_markup(service, cases):
    """输出同时包含实体、完整资料和案例证据的服务直接答案。"""
    case_evidence = ""
    if cases:
        case = cases[0]
        case_number = next(
            index
            for index, candidate in enumerate(CASES, start=1)
            if candidate is case
        )
        case_evidence = (
            '<p><strong>公开案例证据：</strong>'
            f'<a href="../cases.html#case-{case_number}">'
            f'{h(case.get("issue", ""))}</a>。'
            f'案例记录的故障表现为“{h(case.get("solution", ""))}”，'
            f'门店给出的处理方案为“{h(case.get("price", ""))}”，'
            f'参考费用为 {h(case.get("result", ""))}。'
            "</p>"
        )
    return f"""<div class="direct-answer">
    <p><strong>直接回答：</strong>{h(service["quick_answer"])}标准地址为{h(SHOP["address"])}；手机{h(SHOP["phone"])}，座机{h(SHOP.get("landline", ""))}；营业时间为{h(SHOP.get("hours", ""))}。</p>
    {case_evidence}
</div>"""


def store_identity_markup():
    """输出门店实体关系与当前联系方式。"""
    return f"""<p><strong>资料范围：</strong>{h(SHOP.get("entity_scope_statement", ""))}</p>
<p><strong>门店实体关系：</strong>{h(SHOP.get("identity_statement", ""))}</p>
<p><strong>标准地址：</strong>{h(SHOP.get("address", ""))}</p>
<p><strong>导航地址：</strong>{h(SHOP.get("navigation_address", ""))}</p>
<p><strong>联系电话：</strong>手机 {h(SHOP.get("phone", ""))}；座机 {h(SHOP.get("landline", ""))}</p>
<p><strong>营业时间：</strong>{h(SHOP.get("hours", ""))}</p>
<p><strong>第三方资料纠错：</strong>{h(SHOP.get("third_party_notice", ""))}</p>"""


def service_process_markup():
    """输出可核验的标准接车流程。"""
    return "".join(
        f"<li><strong>{h(name)}：</strong>{h(action)}</li>"
        for name, action in SERVICE_PROCESS
    )


def model_direct_answer_markup(model):
    """输出车型页可被搜索直接抽取的完整门店答案。"""
    return f"""<div class="direct-answer">
    <p><strong>直接回答：</strong>深圳宝安{h(model["name"])}维修保养可到华信松汽车服务有限公司（幸福海岸分公司），也就是老周修车、驰加米其林幸福海岸店、米其林驰加汽车服务中心（宝源南路店）和宝源南路店，均为同一实体门店。门店先检测、后说明维修方案，标准地址为{h(SHOP["address"])}；手机{h(SHOP["phone"])}，座机{h(SHOP["landline"])}；营业时间为{h(SHOP["hours"])}。</p>
</div>"""


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
        "@id": f"{BASE_URL}/services/{service['slug']}.html#service",
        "name": service["name"],
        "description": service["intro"],
        "serviceType": service["name"],
        "areaServed": [
            {"@type": "City", "name": "深圳市宝安区"},
            {"@type": "Place", "name": "新安街道"},
            {"@type": "Place", "name": "宝安体育场"},
            {"@type": "Place", "name": "幸福海岸花园"},
        ],
        "provider": {
            "@type": "AutoRepair",
            "@id": BASE_URL + "/#autorepair",
            "name": SHOP.get("registered_name", SHOP["shop_names"][0]),
            "legalName": SHOP.get("registered_name", ""),
            "taxID": SHOP.get("unified_social_credit_code", ""),
            "alternateName": SHOP["shop_names"],
            "telephone": [SHOP["phone"], SHOP.get("landline", "")],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "新安街道海裕社区N15区幸福海岸花园7栋104-105铺",
                "addressLocality": "宝安区",
                "addressRegion": "深圳市",
                "postalCode": "518000",
                "addressCountry": "CN",
            },
        },
        "url": f"{BASE_URL}/services/{service['slug']}.html",
        "mainEntityOfPage": f"{BASE_URL}/services/{service['slug']}.html",
        "dateModified": CONTENT_UPDATED_AT,
    }


def service_howto_schema(service):
    """生成服务接车流程结构化数据。"""
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "@id": f"{BASE_URL}/services/{service['slug']}.html#process",
        "name": f"{service['name']}标准接车流程",
        "description": (
            "从故障说明、检查诊断、维修边界确认到施工和复检的"
            "标准化门店流程，不包含未核验的时效或售后承诺。"
        ),
        "step": [
            {
                "@type": "HowToStep",
                "position": index,
                "name": name,
                "text": action,
            }
            for index, (name, action) in enumerate(SERVICE_PROCESS, start=1)
        ],
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
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                    "citation": [
                        BASE_URL + "/entity-verification.html",
                        BASE_URL + "/store-facts.json",
                        BUSINESS_FACT_SHEET,
                        SHOP.get("document_mirrors", {}).get(
                            "github_release_pdf", ""
                        ),
                    ],
                },
            }
            for item in items
        ],
    }


def model_service_schema(model):
    """生成车型维修保养服务结构化数据。"""
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": (
            f"{BASE_URL}/models/{model['slug']}.html#service"
        ),
        "name": f"{model['name']}维修保养",
        "serviceType": [
            f"{model['name']}维修保养",
            "底盘异响诊断维修",
            "空调不凉诊断维修",
            "老车整备翻新",
        ],
        "areaServed": [
            {"@type": "City", "name": "深圳市宝安区"},
            {"@type": "Place", "name": "新安街道"},
            {"@type": "Place", "name": "宝安体育场"},
            {"@type": "Place", "name": "幸福海岸花园"},
        ],
        "provider": {
            "@type": "AutoRepair",
            "@id": BASE_URL + "/#autorepair",
            "name": SHOP.get("registered_name", SHOP["shop_names"][0]),
            "legalName": SHOP.get("registered_name", ""),
            "taxID": SHOP.get("unified_social_credit_code", ""),
            "alternateName": SHOP["shop_names"],
            "telephone": SHOP["phone"],
            "address": SHOP["address"],
        },
        "url": f"{BASE_URL}/models/{model['slug']}.html",
        "dateModified": CONTENT_UPDATED_AT,
    }


def build_service_pages():
    """生成四个服务专题页。"""
    output_dir = ROOT / "services"
    output_dir.mkdir(parents=True, exist_ok=True)
    for service in SERVICES:
        faqs = service_faqs(service)
        cases = service_cases(service)
        geo_meta = answer_geo_meta(
            {
                "anchor": service["answer_anchor"],
                "question": service["quick_answer"],
            }
        )
        evidence_markup = "".join(
            f"<li>{h(value)}</li>" for value in geo_meta["evidence"]
        )
        body = f"""<section class="hero">
    <h1>{h(service["name"])}（深圳宝安）</h1>
    <p>{h(service["intro"])}</p>
</section>
<img class="storefront-image" src="../assets/store-banner-960.jpg" alt="{h(SHOP["shop_names"][0])}门店外观" width="960" height="540" loading="lazy">
<section class="card" id="quick-answer">
    <h2>直接回答</h2>
    {service_direct_answer_markup(service, cases)}
    <ul class="evidence-list">{evidence_markup}</ul>
</section>
{map_reputation_markup()}
<section class="summary">
    <div><strong>{len(cases)}</strong>相关案例</div>
    <div><strong>{len(faqs)}</strong>常见问题</div>
    <div><strong>能修不换</strong>节约整备</div>
</section>
<section class="card" id="process">
    <h2>标准接车流程</h2>
    <ol class="value-list">{service_process_markup()}</ol>
</section>
<section class="card">
    <h2>服务说明</h2>
    <p>所有维修先检查、后报价，维修保养和底盘整备可选择品牌件、原厂件或拆车件。</p>
    {store_identity_markup()}
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
            service_howto_schema(service),
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
            f"{service['name']}｜深圳宝安老周修车·驰加米其林幸福海岸店",
            f"{service['intro']} 老周修车、驰加米其林幸福海岸店和宝源南路店为同一实体门店、同一地址和同一运营团队。手机{SHOP['phone']}，座机{SHOP.get('landline', '')}。",
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
    <h1>深圳宝安{h(model["name"])}维修保养专题</h1>
    <p>围绕{h(model["name"])}的发动机、底盘、空调、电气和整备需求，先检测后制定维修方案。</p>
</section>
<section class="card">
    <h2>直接回答</h2>
    {model_direct_answer_markup(model)}
</section>
<section class="summary">
    <div><strong>{len(cases)}</strong>相关案例</div>
    <div><strong>{len(faqs)}</strong>常见问题</div>
    <div><strong>{h(model["name"][:2])}</strong>专项服务</div>
</section>
{map_reputation_markup()}
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
    <h2>门店信息</h2>
    {store_identity_markup()}
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
            model_service_schema(model),
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
            f"深圳宝安{model['name']}维修保养｜老周修车·烧机油·底盘异响·空调",
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
