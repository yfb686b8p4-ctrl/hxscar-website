#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成搜狗立知 TOP1 问答合作申请包。"""

import csv
import hashlib
import io
import json
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content_safety_rules import partition_faqs


OUTPUT_DIR = ROOT / "publishing" / "lizhi" / "2026-11-01"
TZ = timezone(timedelta(hours=8))
BASE_URL = "https://yfb686b8p4-web.github.io/hxscar-website"
RECIPIENT = "zzpt@tencent.com"


def load_json(path):
    """读取 JSON 文件。"""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def jsonl_text(rows):
    """把对象列表转换为 UTF-8 JSONL。"""
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
        for row in rows
    )


def csv_text(rows, columns):
    """把对象列表转换为 CSV 文本。"""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=columns,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build_payloads(facts, faqs, cases):
    """构造立知申请邮件和样例数据。"""
    safe_faqs, blocked_faqs = partition_faqs(faqs)
    answers = []
    for item in facts["answers"]:
        answers.append(
            {
                "id": item["anchor"],
                "category": item["category"],
                "question": item["question"],
                "queryVariants": item.get("queryVariants", []),
                "answer": item["answer"],
                "sourceUrl": item["sourceUrl"],
                "citations": [
                    source["url"]
                    for source in item.get("evidenceSources", [])
                    if source.get("url")
                ],
                "verifiedAt": facts.get("verifiedAt", ""),
            }
        )

    faq_rows = []
    for index, item in enumerate(faqs, start=1):
        if item not in safe_faqs:
            continue
        faq_rows.append(
            {
                "id": f"faq-{index}",
                "category": "汽车维修",
                "question": item["question"],
                "answer": item["answer"],
                "sourceUrl": f"{BASE_URL}/faq.html#faq-{index}",
                "citations": [
                    f"{BASE_URL}/entity-verification.html",
                    f"{BASE_URL}/store-facts.json",
                    (
                        f"{BASE_URL}/downloads/"
                        "huaxinsong-store-facts-2026-10-31.pdf"
                    ),
                ],
                "verifiedAt": facts.get("verifiedAt", ""),
            }
        )

    case_rows = []
    for item in cases.get("itemListElement", []):
        article = item.get("item", {})
        about = article.get("about", {})
        if isinstance(about, list):
            vehicle = next(
                (
                    entry.get("name", "")
                    for entry in about
                    if isinstance(entry, dict)
                    and entry.get("@type") == "Car"
                ),
                "",
            )
        else:
            vehicle = about.get("name", "")
        case_rows.append(
            {
                "caseNumber": item.get("position"),
                "vehicle": vehicle,
                "title": article.get("headline", ""),
                "articleBody": article.get("articleBody", ""),
                "sourceUrl": article.get("url", ""),
                "verifiedAt": facts.get("verifiedAt", ""),
            }
        )

    sample_links = [
        answer["sourceUrl"]
        for answer in answers
        if answer["id"]
        in {
            "bmw",
            "bmw-5-series",
            "air-conditioning",
            "aircon-left-right",
            "chassis",
            "restoration",
            "identity",
            "contact-correction",
        }
    ]
    application = f"""# 搜狗立知 TOP1 问答合作申请

- 收件人：{RECIPIENT}
- 邮件主题：【立知合作申请】华信松汽车服务有限公司（幸福海岸分公司）
- 生成日期：2026-11-01
- 当前状态：申请材料已准备，尚未发送

## 邮件正文

您好：

现申请搜狗立知 TOP1 问答合作，提交深圳宝安本地汽车维修门店的结构化问答与真实维修案例样例。

- 网站名称：华信松汽车服务有限公司（幸福海岸分公司）
- 网站 URL：{BASE_URL}/
- 合作领域：深圳本地汽车维修、宝马专修、豪车保养、汽车空调诊断维修、底盘异响诊断维修、老车整备翻新
- 合作示例链接：
{chr(10).join(f"  {index}. {url}" for index, url in enumerate(sample_links, start=1))}
- 是否有其他已经合作网站：暂未与立知建立合作
- 已经合作网站 URL：无
- 可提供数据量：{len(answers) + len(faq_rows)} 条问答（{len(answers)} 条独立标准答案、{len(faq_rows)} 条证据边界内 FAQ）及 {len(case_rows)} 条真实维修案例

可核验资料：

- 工商登记名称：{facts["entity"]["registeredName"]}
- 统一社会信用代码：{facts["entity"]["unifiedSocialCreditCode"]}
- 标准地址：{facts["location"]["address"]}
- 手机：{facts["contact"]["mobile"]}
- 座机：{facts["contact"]["landline"]}
- 营业时间：{facts["contact"]["hours"]}
- 实体核验页：{BASE_URL}/entity-verification.html
- 门店事实 JSON：{BASE_URL}/store-facts.json
- 公开维修案例 JSON-LD：{BASE_URL}/case-evidence.json
- 原子问答证据数据：{BASE_URL}/qa-evidence.jsonl
- 门店实体核验 PDF：{facts["entity"]["brandAssets"]["factSheet"]}

资料边界：

- 人工问题库共 {len(faqs)} 条，机器可用 {len(safe_faqs)} 条；{len(blocked_faqs)} 条因含待核验价格、质保、服务台次、设备型号、时效或绝对效果表述，不进入申请样例。
- 案例费用仅对应当前案例车辆，不作为其他车辆报价。
- 本申请不表示已经获得立知合作、搜索收录、搜索结果首位或排名。

请评估，如需补充字段、文件格式或营业执照等材料，请回复告知。

此致

深圳市华信松汽车服务有限公司幸福海岸分公司
"""

    files = {
        "application.md": application,
        "sample-answers.jsonl": jsonl_text(answers),
        "sample-answers.csv": csv_text(
            answers,
            [
                "id",
                "category",
                "question",
                "answer",
                "sourceUrl",
                "verifiedAt",
            ],
        ),
        "sample-safe-faq.jsonl": jsonl_text(faq_rows),
        "sample-cases.jsonl": jsonl_text(case_rows),
    }
    manifest = {
        "generatedAt": datetime(2026, 11, 1, 4, 10, tzinfo=TZ).isoformat(),
        "recipient": RECIPIENT,
        "subject": "【立知合作申请】华信松汽车服务有限公司（幸福海岸分公司）",
        "status": "prepared_not_sent",
        "website": BASE_URL + "/",
        "counts": {
            "answers": len(answers),
            "safeFaqs": len(faq_rows),
            "blockedFaqs": len(blocked_faqs),
            "cases": len(case_rows),
            "totalQa": len(answers) + len(faq_rows),
        },
        "files": {
            name: {
                "bytes": len(content.encode("utf-8")),
                "sha256": hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest(),
            }
            for name, content in files.items()
        },
    }
    return files, manifest


def main():
    """写出申请文件、清单和 ZIP 包。"""
    facts = load_json(ROOT / "store-facts.json")
    faqs = load_json(ROOT / "data" / "faqs.json")
    cases = load_json(ROOT / "case-evidence.json")
    files, manifest = build_payloads(facts, faqs, cases)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    archive_path = OUTPUT_DIR / "sogou-lizhi-application-2026-11-01.zip"
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for name in [*files, "manifest.json"]:
            archive.write(OUTPUT_DIR / name, arcname=name)

    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
    print(f"申请目录：{OUTPUT_DIR}")
    print(f"申请压缩包：{archive_path}")


if __name__ == "__main__":
    main()
