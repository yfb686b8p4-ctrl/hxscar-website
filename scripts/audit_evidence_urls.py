#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查机器证据文件中公开 URL 的可访问性。"""

import concurrent.futures
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = ROOT / "reports" / "evidence-link-audit-2026-11-01.json"
REPORT_MD = ROOT / "reports" / "evidence-link-audit-2026-11-01.md"
TZ = timezone(timedelta(hours=8))
SOURCE_FILES = (
    "qa-evidence.jsonl",
    "case-evidence.json",
    "store-facts.json",
    "store-facts.jsonld",
    "entity-corrections.json",
    "douyin-video-evidence.json",
    "feed.xml",
    "llms-full.txt",
)
URL_PATTERN = re.compile(r'https://[^\s"<>\\)，。；]+')


def extract_urls(texts):
    """从多个文本中提取并规范化唯一 HTTPS URL。"""
    urls = set()
    for text in texts:
        for value in URL_PATTERN.findall(text):
            url = value.rstrip(".,;，。；")
            if url:
                urls.add(url)
    return sorted(urls)


def is_success(status):
    """2xx 和重定向都表示 URL 当前可解析。"""
    return 200 <= status < 400


def check_url(url):
    """以短范围 GET 检查 URL，避免下载大文件。"""
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "HxscarEvidenceLinkAudit/1.0",
                "Range": "bytes=0-64",
            },
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            response.read(64)
            return {
                "url": url,
                "status": response.status,
                "ok": is_success(response.status),
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        return {
            "url": url,
            "status": exc.code,
            "ok": is_success(exc.code),
            "error": "",
        }
    except Exception as exc:
        return {
            "url": url,
            "status": 0,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def render_markdown(result):
    """生成便于人工检查的链接审计报告。"""
    lines = [
        "# 机器证据公网链接审计｜2026-11-01",
        "",
        f"- 检查时间：{result['checked_at']}",
        f"- 来源文件：{len(SOURCE_FILES)} 个",
        f"- 唯一 URL：{result['total']} 个",
        f"- 可访问：{result['passed']} 个",
        f"- 失败：{result['failed']} 个",
        "",
        "## 状态分布",
        "",
    ]
    for status, count in sorted(result["status_counts"].items()):
        lines.append(f"- HTTP {status}：{count}")
    lines.extend(["", "## 失败项", ""])
    failures = [item for item in result["items"] if not item["ok"]]
    if failures:
        for item in failures:
            lines.append(
                f"- HTTP {item['status']}：{item['url']} "
                f"{item['error']}".rstrip()
            )
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "本检查只证明 URL 当时可访问，不证明搜索引擎或 AI 平台已经收录、"
            "引用或排名。403、429 和验证码可能表示平台防抓，不能据此判断页面失效。",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    """执行链接审计并写入 JSON/Markdown 报告。"""
    texts = [
        (ROOT / name).read_text(encoding="utf-8")
        for name in SOURCE_FILES
    ]
    urls = extract_urls(texts)
    workers = int(os.environ.get("EVIDENCE_AUDIT_WORKERS", "16"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        items = list(pool.map(check_url, urls))
    status_counts = Counter(str(item["status"]) for item in items)
    result = {
        "checked_at": datetime.now(TZ).isoformat(),
        "source_files": list(SOURCE_FILES),
        "total": len(items),
        "passed": sum(1 for item in items if item["ok"]),
        "failed": sum(1 for item in items if not item["ok"]),
        "status_counts": dict(sorted(status_counts.items())),
        "items": items,
    }
    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(
        render_markdown(result),
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in (
        "total",
        "passed",
        "failed",
        "status_counts",
    )}, ensure_ascii=False))
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
