#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核验官网、Profile、Release 和 Gist 的原子问答镜像。"""

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content_safety_rules import unverified_claim_markers


REPORT_JSON = ROOT / "reports" / "mirror-consistency-2026-11-01.json"
REPORT_MD = ROOT / "reports" / "mirror-consistency-2026-11-01.md"
TZ = timezone(timedelta(hours=8))
EXPECTED_QA_ROWS = 16
MIRRORS = [
    {
        "name": "本地构建",
        "path": "qa-evidence.jsonl",
    },
    {
        "name": "官网",
        "url": (
            "https://yfb686b8p4-web.github.io/"
            "hxscar-website/qa-evidence.jsonl"
        ),
    },
    {
        "name": "Profile Pages",
        "url": (
            "https://yfb686b8p4-web.github.io/"
            "yfb686b8p4-web/qa-evidence.jsonl"
        ),
    },
    {
        "name": "GitHub Release",
        "url": (
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "qa-evidence.jsonl?v=20261101-v5"
        ),
    },
    {
        "name": "GitHub Gist",
        "url": (
            "https://gist.githubusercontent.com/yfb686b8p4-web/"
            "7923ef0b18ffbcce04a8b6758254a06b/raw/"
            "qa-evidence.jsonl?v=20261101-cdn-v5"
        ),
    },
    {
        "name": "jsDelivr",
        "url": (
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/"
            "hxscar-website@ai-evidence-cdn-2026-11-01-v8/"
            "qa-evidence.jsonl"
        ),
    },
]
FACT_MIRRORS = [
    {
        "name": "本地门店事实",
        "kind": "facts",
        "path": "store-facts.json",
    },
    {
        "name": "本地门店JSON-LD",
        "kind": "jsonld",
        "path": "store-facts.jsonld",
    },
    {
        "name": "官网门店事实",
        "kind": "facts",
        "url": (
            "https://yfb686b8p4-web.github.io/"
            "hxscar-website/store-facts.json"
        ),
    },
    {
        "name": "Release门店事实",
        "kind": "facts",
        "url": (
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "store-facts.json?v=20261101-v5"
        ),
    },
    {
        "name": "官网门店JSON-LD",
        "kind": "jsonld",
        "url": (
            "https://yfb686b8p4-web.github.io/"
            "hxscar-website/store-facts.jsonld"
        ),
    },
    {
        "name": "Release门店JSON-LD",
        "kind": "jsonld",
        "url": (
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "store-facts.jsonld?v=20261101-v5"
        ),
    },
    {
        "name": "Gist门店JSON-LD",
        "kind": "jsonld",
        "url": (
            "https://gist.githubusercontent.com/yfb686b8p4-web/"
            "7923ef0b18ffbcce04a8b6758254a06b/raw/"
            "store-facts.jsonld?v=20261101-cdn-v5"
        ),
    },
    {
        "name": "jsDelivr门店事实",
        "kind": "facts",
        "url": (
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/"
            "hxscar-website@ai-evidence-cdn-2026-11-01-v8/"
            "store-facts.json"
        ),
    },
    {
        "name": "jsDelivr门店JSON-LD",
        "kind": "jsonld",
        "url": (
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/"
            "hxscar-website@ai-evidence-cdn-2026-11-01-v8/"
            "store-facts.jsonld"
        ),
    },
]
CORRECTION_MIRRORS = [
    {
        "name": "本地门店纠错JSON",
        "path": "entity-corrections.json",
    },
    {
        "name": "官网门店纠错JSON",
        "url": (
            "https://yfb686b8p4-web.github.io/"
            "hxscar-website/entity-corrections.json"
        ),
    },
    {
        "name": "Profile门店纠错JSON",
        "url": (
            "https://yfb686b8p4-web.github.io/"
            "yfb686b8p4-web/entity-corrections.json"
        ),
    },
    {
        "name": "Release门店纠错JSON",
        "url": (
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "entity-corrections.json?v=20261101-v5"
        ),
    },
    {
        "name": "Gist门店纠错JSON",
        "url": (
            "https://gist.githubusercontent.com/yfb686b8p4-web/"
            "7923ef0b18ffbcce04a8b6758254a06b/raw/"
            "entity-corrections.json?v=20261101-cdn-v5"
        ),
    },
    {
        "name": "jsDelivr门店纠错JSON",
        "url": (
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/"
            "hxscar-website@ai-evidence-cdn-2026-11-01-v8/"
            "entity-corrections.json"
        ),
    },
]


def fetch_bytes(url, timeout=30):
    """读取公开镜像的原始字节。"""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "HxscarMirrorVerifier/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def read_mirror_bytes(mirror):
    """读取本地构建或远端镜像字节。"""
    if mirror.get("path"):
        return (ROOT / mirror["path"]).read_bytes()
    return fetch_bytes(mirror["url"])


def evaluate_qa_payload(payload):
    """解析并验证单个 JSONL 问答镜像。"""
    text = payload.decode("utf-8")
    rows = [
        json.loads(line)
        for line in text.splitlines()
        if line.strip()
    ]
    errors = []
    ids = []
    with_cases = 0
    min_citations = 10**9
    for row in rows:
        if row.get("@type") != "Question" or not row.get("name"):
            errors.append("存在无效 Question")
            continue
        ids.append(row.get("@id", ""))
        answer = row.get("acceptedAnswer", {})
        citations = answer.get("citation", [])
        if answer.get("@type") != "Answer" or not answer.get("text"):
            errors.append(f"缺少直接答案：{row.get('name', '')}")
        if len(citations) < 4:
            errors.append(f"引用不足：{row.get('name', '')}")
        if any(
            not str(url).startswith("https://")
            for url in citations
        ):
            errors.append(f"引用不是 HTTPS：{row.get('name', '')}")
        if unverified_claim_markers(
            row.get("name", "") + answer.get("text", "")
        ):
            errors.append(f"含未核实承诺：{row.get('name', '')}")
        if row.get("caseEvidence"):
            with_cases += 1
        min_citations = min(min_citations, len(citations))
    if len(rows) != EXPECTED_QA_ROWS:
        errors.append(
            f"问答数量应为 {EXPECTED_QA_ROWS}，实际为 {len(rows)}"
        )
    if len(set(ids)) != len(ids):
        errors.append("Question @id 存在重复")
    return {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "rows": len(rows),
        "unique_ids": len(set(ids)),
        "with_cases": with_cases,
        "min_citations": (
            min_citations if min_citations != 10**9 else 0
        ),
        "errors": errors,
    }


def evaluate_fact_payload(payload, kind):
    """解析并验证门店事实 JSON 或 AutoRepair JSON-LD。"""
    data = json.loads(payload.decode("utf-8"))
    errors = []
    if kind == "facts":
        if data.get("schemaVersion") != "1.1":
            errors.append("门店事实 schemaVersion 不是 1.1")
        entity = data.get("entity", {})
        if entity.get("unifiedSocialCreditCode") != "91440300MA5GYCTQ6P":
            errors.append("门店事实统一社会信用代码不正确")
        if len(data.get("answers", [])) != EXPECTED_QA_ROWS:
            errors.append(
                "门店事实答案数量不是 "
                f"{EXPECTED_QA_ROWS}"
            )
    elif kind == "jsonld":
        if data.get("@type") != "AutoRepair":
            errors.append("JSON-LD 顶层类型不是 AutoRepair")
        if data.get("taxID") != "91440300MA5GYCTQ6P":
            errors.append("JSON-LD 统一社会信用代码不正确")
        catalog = data.get("hasOfferCatalog", {})
        if catalog.get("@type") != "OfferCatalog":
            errors.append("JSON-LD 缺少 OfferCatalog")
        if catalog.get("numberOfItems") != 4:
            errors.append("JSON-LD 服务目录不是 4 项")
    else:
        errors.append(f"未知验证类型：{kind}")
    return {
        "kind": kind,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "errors": errors,
    }


def evaluate_correction_payload(payload):
    """解析并验证门店历史资料纠正 JSON。"""
    data = json.loads(payload.decode("utf-8"))
    errors = []
    if data.get("schemaVersion") != "1.0":
        errors.append("门店纠错 schemaVersion 不是 1.0")
    if data.get("documentType") != "BusinessEntityFactCorrection":
        errors.append("门店纠错 documentType 不正确")
    current = data.get("currentFacts", {})
    expected = {
        "registeredName": "深圳市华信松汽车服务有限公司幸福海岸分公司",
        "unifiedSocialCreditCode": "91440300MA5GYCTQ6P",
        "mobile": "18682417667",
        "landline": "0755-23340534",
        "openingHours": "周一至周五 08:00-18:00；周六日 09:00-17:00",
    }
    for key, value in expected.items():
        if current.get(key) != value:
            errors.append(f"门店纠错当前值错误：{key}")
    fields = {
        item.get("field")
        for item in data.get("correctedFields", [])
    }
    if fields != {"telephone", "openingHours", "address"}:
        errors.append("门店纠错字段不完整")
    if len(data.get("evidence", [])) < 4:
        errors.append("门店纠错证据入口不足")
    return {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "errors": errors,
    }


def verify_mirrors():
    """下载四个镜像并生成一致性结果。"""
    results = []
    for mirror in MIRRORS:
        item = {
            "name": mirror["name"],
            "url": mirror.get("url", ""),
            "path": mirror.get("path", ""),
        }
        try:
            item.update(
                evaluate_qa_payload(read_mirror_bytes(mirror))
            )
        except Exception as exc:
            item.update(
                {
                    "bytes": 0,
                    "sha256": "",
                    "rows": 0,
                    "unique_ids": 0,
                    "with_cases": 0,
                    "min_citations": 0,
                    "errors": [f"{type(exc).__name__}: {exc}"],
                }
            )
        results.append(item)

    fact_results = []
    for mirror in FACT_MIRRORS:
        item = {
            "name": mirror["name"],
            "kind": mirror["kind"],
            "url": mirror.get("url", ""),
            "path": mirror.get("path", ""),
        }
        try:
            item.update(
                evaluate_fact_payload(
                    read_mirror_bytes(mirror),
                    mirror["kind"],
                )
            )
        except Exception as exc:
            item.update(
                {
                    "bytes": 0,
                    "sha256": "",
                    "errors": [f"{type(exc).__name__}: {exc}"],
                }
            )
        fact_results.append(item)

    correction_results = []
    for mirror in CORRECTION_MIRRORS:
        item = {
            "name": mirror["name"],
            "url": mirror.get("url", ""),
            "path": mirror.get("path", ""),
        }
        try:
            item.update(
                evaluate_correction_payload(read_mirror_bytes(mirror))
            )
        except Exception as exc:
            item.update(
                {
                    "bytes": 0,
                    "sha256": "",
                    "errors": [f"{type(exc).__name__}: {exc}"],
                }
            )
        correction_results.append(item)

    hashes = {item["sha256"] for item in results}
    fact_hashes = {
        kind: {
            item["sha256"]
            for item in fact_results
            if item["kind"] == kind
        }
        for kind in ("facts", "jsonld")
    }
    correction_hashes = {
        item["sha256"] for item in correction_results
    }
    consistency_errors = []
    if len(hashes) != 1:
        consistency_errors.append("问答镜像 SHA-256 不一致")
    if len(fact_hashes["facts"]) != 1:
        consistency_errors.append("门店事实 SHA-256 不一致")
    if len(fact_hashes["jsonld"]) != 1:
        consistency_errors.append("门店 JSON-LD SHA-256 不一致")
    if len(correction_hashes) != 1:
        consistency_errors.append("门店纠错 JSON SHA-256 不一致")
    if any(
        item["errors"]
        for item in results + fact_results + correction_results
    ):
        consistency_errors.append("至少一个镜像未通过结构校验")
    consistent = (
        len(hashes) == 1
        and all(not item["errors"] for item in results)
        and all(item["rows"] == EXPECTED_QA_ROWS for item in results)
        and len(fact_hashes["facts"]) == 1
        and len(fact_hashes["jsonld"]) == 1
        and all(not item["errors"] for item in fact_results)
        and len(correction_hashes) == 1
        and all(not item["errors"] for item in correction_results)
    )
    return {
        "checked_at": datetime.now(TZ).date().isoformat(),
        "consistent": consistent,
        "expected_rows": EXPECTED_QA_ROWS,
        "unique_hashes": len(hashes),
        "consistencyErrors": consistency_errors,
        "mirrors": results,
        "factMirrors": fact_results,
        "correctionMirrors": correction_results,
        "factUniqueHashes": {
            kind: len(values)
            for kind, values in fact_hashes.items()
        },
        "correctionUniqueHashes": len(correction_hashes),
    }


def write_report(result):
    """写入 JSON 与 Markdown 核验报告。"""
    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# AI 证据镜像一致性核验｜2026-11-01",
        "",
        f"- 核验时间：{result['checked_at']}",
        f"- 一致性：{'通过' if result['consistent'] else '未通过'}",
        f"- 唯一 SHA-256 数量：{result['unique_hashes']}",
        f"- 每个镜像预期问答数：{result['expected_rows']}",
        (
            "- 门店事实唯一哈希："
            f"{result['factUniqueHashes']['facts']}"
        ),
        (
            "- JSON-LD 唯一哈希："
            f"{result['factUniqueHashes']['jsonld']}"
        ),
        (
            "- 门店纠错 JSON 唯一哈希："
            f"{result['correctionUniqueHashes']}"
        ),
        "",
        "| 镜像 | 行数 | 唯一ID | 带案例 | 最少引用 | SHA-256 | 状态 |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for item in result["mirrors"]:
        status = "通过" if not item["errors"] else "失败"
        lines.append(
            f"| {item['name']} | {item['rows']} | "
            f"{item['unique_ids']} | {item['with_cases']} | "
            f"{item['min_citations']} | `{item['sha256'][:16]}…` | "
            f"{status} |"
        )
    lines.extend(
        [
            "",
            "## 门店事实与实体镜像",
            "",
            "| 镜像 | 类型 | SHA-256 | 状态 |",
            "|---|---|---|---|",
        ]
    )
    for item in result["factMirrors"]:
        status = "通过" if not item["errors"] else "失败"
        lines.append(
            f"| {item['name']} | {item['kind']} | "
            f"`{item['sha256'][:16]}…` | {status} |"
        )
    lines.extend(
        [
            "",
            "## 门店历史资料纠正镜像",
            "",
            "| 镜像 | SHA-256 | 状态 |",
            "|---|---|---|",
        ]
    )
    for item in result["correctionMirrors"]:
        status = "通过" if not item["errors"] else "失败"
        lines.append(
            f"| {item['name']} | `{item['sha256'][:16]}…` | {status} |"
        )
    lines.extend(["", "## 错误", ""])
    errors = [
        f"{item['name']}：{error}"
        for item in result["mirrors"]
        for error in item["errors"]
    ] + [
        f"{item['name']}：{error}"
        for item in result["factMirrors"]
        for error in item["errors"]
    ] + [
        f"{item['name']}：{error}"
        for item in result["correctionMirrors"]
        for error in item["errors"]
    ] + result["consistencyErrors"]
    lines.extend(f"- {error}" for error in errors) if errors else lines.append("- 无")
    lines.extend(
        [
            "",
            "本核验只证明公开文件字节一致且结构满足要求，"
            "不代表任何搜索引擎或 AI 平台已经收录、引用或排名。",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    """执行核验并输出摘要。"""
    result = verify_mirrors()
    write_report(result)
    print(
        json.dumps(
            {
                "consistent": result["consistent"],
                "unique_hashes": result["unique_hashes"],
                "mirrors": len(result["mirrors"]),
                "report": str(REPORT_MD.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not result["consistent"]:
        raise SystemExit("AI 证据镜像不一致")


if __name__ == "__main__":
    main()
