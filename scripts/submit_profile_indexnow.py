#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交 GitHub Profile 实体镜像页到 IndexNow。"""

import argparse
import json
import subprocess
import time
import urllib.request

try:
    from submit_indexnow import ENDPOINTS, HOST, submit_payload
except ModuleNotFoundError:
    from scripts.submit_indexnow import ENDPOINTS, HOST, submit_payload


KEY = "hxscarprofile20261101geo"
KEY_LOCATION = (
    f"https://{HOST}/yfb686b8p4-web/{KEY}.txt"
)
URLS = [
    f"https://{HOST}/yfb686b8p4-web/",
    f"https://{HOST}/yfb686b8p4-web/answers.html",
    f"https://{HOST}/yfb686b8p4-web/qa-evidence.jsonl",
    f"https://{HOST}/yfb686b8p4-web/douyin-video-evidence.json",
    f"https://{HOST}/yfb686b8p4-web/entity-corrections.json",
    f"https://{HOST}/yfb686b8p4-web/robots.txt",
    f"https://{HOST}/yfb686b8p4-web/llms.txt",
    f"https://{HOST}/yfb686b8p4-web/sitemap.xml",
    f"https://{HOST}/yfb686b8p4-web/image-sitemap.xml",
    f"https://{HOST}/yfb686b8p4-web/assets/store-banner.jpg",
    f"https://{HOST}/yfb686b8p4-web/assets/store-avatar-300.jpg",
]


def wait_for_key(attempts=6, delay=10):
    """等待 Profile Pages 发布验证文件。"""
    for attempt in range(1, attempts + 1):
        try:
            result = subprocess.run(
                [
                    "curl",
                    "--http1.1",
                    "--silent",
                    "--show-error",
                    "--max-time",
                    "15",
                    KEY_LOCATION,
                ],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                raise OSError(
                    result.stderr.decode("utf-8", "ignore").strip()
                    or f"curl 退出码 {result.returncode}"
                )
            content = result.stdout.decode("utf-8", "ignore").strip()
            if content == KEY:
                print(f"Profile IndexNow 验证文件已上线，第 {attempt} 次检查通过")
                return True
        except OSError as exc:
            print(f"等待 Profile 验证文件 {attempt}/{attempts}: {exc}")
        if attempt < attempts:
            time.sleep(delay)
    return False


def main():
    """提交 Profile Pages 请求。"""
    parser = argparse.ArgumentParser(description="提交 Profile 实体页到 IndexNow")
    parser.add_argument("--dry-run", action="store_true", help="只打印请求")
    parser.add_argument("--wait", action="store_true", help="等待验证文件上线")
    args = parser.parse_args()

    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URLS,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if args.wait and not wait_for_key():
        raise SystemExit("Profile IndexNow 验证文件尚未上线，本次跳过")

    results = []
    for name, endpoint in ENDPOINTS:
        try:
            status = submit_payload(payload, endpoint)
        except OSError as exc:
            print(f"{name} 提交失败: {exc}")
            continue
        results.append((name, status))
        print(f"{name} HTTP {status}: {len(URLS)} 个 URL")
    if not results:
        raise SystemExit("所有 Profile IndexNow 提交端点均失败")


if __name__ == "__main__":
    main()
