#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查机器证据文件中公开 URL 的可访问性。"""

import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time
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
BLOCKED_STATUSES = {401, 403, 405, 429}
VOLATILE_MIRROR_HOSTS = {
    "r.jina.ai",
    "web.archive.org",
    "www.qcc.com",
}
PROXY_URL = os.environ.get(
    "EVIDENCE_AUDIT_PROXY",
    "http://127.0.0.1:7897",
)


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


def is_blocked(status, url=""):
    """平台防抓状态单独记录，不当作坏链。"""
    if status in BLOCKED_STATUSES:
        return True
    if (
        any(f"//{host}/" in url for host in VOLATILE_MIRROR_HOSTS)
        and status in {0, 404}
    ):
        return True
    return False


def curl_command(url, proxy=""):
    """构造一次 URL 可达性检查命令。"""
    command = [
        "curl",
        "-L",
        "--compressed",
        "--silent",
        "--show-error",
        "--max-time",
        "20",
        "--output",
        os.devnull,
        "--write-out",
        "%{http_code}",
    ]
    if proxy:
        command.extend(["--proxy", proxy])
    command.append(url)
    return command


def run_curl(url, proxy=""):
    """执行一次 curl 并解析状态码。"""
    result = subprocess.run(
        curl_command(url, proxy),
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        status = int(result.stdout.strip() or "0")
    except ValueError:
        status = 0
    error = result.stderr.strip() if result.returncode else ""
    return {
        "url": url,
        "status": status,
        "ok": is_success(status),
        "blocked": is_blocked(status, url),
        "error": error[:240],
        "via": "代理" if proxy else "直连",
    }


def check_url(url):
    """直连超时后通过本地代理重试，区分网络失败与真实坏链。"""
    result = run_curl(url)
    if result["ok"] or result["blocked"] or not PROXY_URL:
        return result
    proxied = run_curl(url, PROXY_URL)
    if proxied["ok"] or proxied["blocked"] or proxied["status"]:
        return proxied
    return result


def check_with_retries(url, attempts=3, delay=1):
    """对容易限流的域名串行重试。"""
    result = check_url(url)
    for index in range(1, attempts):
        if result["ok"] or result["blocked"]:
            return result
        time.sleep(delay * index)
        result = check_url(url)
    return result


def render_markdown(result):
    """生成便于人工检查的链接审计报告。"""
    lines = [
        "# 机器证据公网链接审计｜2026-11-01",
        "",
        f"- 检查时间：{result['checked_at']}",
        f"- 来源文件：{len(SOURCE_FILES)} 个",
        f"- 唯一 URL：{result['total']} 个",
        f"- 可访问：{result['passed']} 个",
        f"- 平台防抓：{result['blocked']} 个",
        f"- 失败：{result['failed']} 个",
        "",
        "## 状态分布",
        "",
    ]
    for status, count in sorted(result["status_counts"].items()):
        lines.append(f"- HTTP {status}：{count}")
    lines.extend(["", "## 失败项", ""])
    failures = [
        item
        for item in result["items"]
        if not item["ok"] and not item["blocked"]
    ]
    if failures:
        for item in failures:
            lines.append(
                f"- HTTP {item['status']}：{item['url']} "
                f"{item['error']}".rstrip()
            )
    else:
        lines.append("- 无")
    lines.extend(["", "## 平台防抓项", ""])
    blocked = [
        item for item in result["items"] if item["blocked"]
    ]
    if blocked:
        for item in blocked:
            lines.append(f"- HTTP {item['status']}：{item['url']}")
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
    serial_urls = [
        url for url in urls
        if (
            "web.archive.org/" in url
            or "r.jina.ai/" in url
        )
    ]
    standard_urls = [
        url for url in urls
        if url not in set(serial_urls)
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        standard_items = list(pool.map(check_url, standard_urls))
    serial_items = [
        check_with_retries(url)
        for url in serial_urls
    ]
    items = sorted(
        [*standard_items, *serial_items],
        key=lambda item: item["url"],
    )
    status_counts = Counter(str(item["status"]) for item in items)
    result = {
        "checked_at": datetime.now(TZ).isoformat(),
        "source_files": list(SOURCE_FILES),
        "total": len(items),
        "passed": sum(1 for item in items if item["ok"]),
        "blocked": sum(1 for item in items if item["blocked"]),
        "failed": sum(
            1
            for item in items
            if not item["ok"] and not item["blocked"]
        ),
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
        "blocked",
        "failed",
        "status_counts",
    )}, ensure_ascii=False))
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
