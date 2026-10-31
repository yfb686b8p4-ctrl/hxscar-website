#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 sitemap.xml 提取核心 URL，并通过 IndexNow 提交快速收录请求。"""

import argparse
import json
import subprocess
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KEY = "hxscar20261024geoindexkey"
HOST = "yfb686b8p4-web.github.io"
KEY_LOCATION = f"https://{HOST}/hxscar-website/{KEY}.txt"
ENDPOINTS = (
    ("IndexNow 聚合端点", "https://api.indexnow.org/indexnow"),
    ("Bing 直连端点", "https://www.bing.com/indexnow"),
    ("Yandex 直连端点", "https://yandex.com/indexnow"),
    ("Seznam 直连端点", "https://search.seznam.cz/indexnow"),
    ("Naver 直连端点", "https://searchadvisor.naver.com/indexnow"),
    ("Yep 直连端点", "https://indexnow.yep.com/indexnow"),
)
PRIORITY_PATHS = {
    "/hxscar-website/",
    "/hxscar-website/faq.html",
    "/hxscar-website/cases.html",
    "/hxscar-website/answers.html",
    "/hxscar-website/store-profile.html",
    "/hxscar-website/entity-verification.html",
    "/hxscar-website/evidence-policy.html",
    "/hxscar-website/store-facts.json",
    "/hxscar-website/entity-corrections.json",
    "/hxscar-website/downloads/entity-facts-2026-11-01.md",
    "/hxscar-website/store-facts.jsonld",
    "/hxscar-website/case-evidence.json",
    "/hxscar-website/qa-evidence.jsonl",
    "/hxscar-website/douyin-video-evidence.json",
    "/hxscar-website/feed.xml",
    "/hxscar-website/assets/store-avatar-300.jpg",
    "/hxscar-website/assets/store-banner.jpg",
    "/hxscar-website/assets/store-banner.webp",
    "/hxscar-website/assets/store-banner-960.webp",
    "/hxscar-website/downloads/huaxinsong-store-facts-2026-10-31.pdf",
    "/hxscar-website/llms.txt",
    "/hxscar-website/llms-full.txt",
    "/hxscar-website/robots.txt",
    "/hxscar-website/sitemap-index.xml",
    "/hxscar-website/services/index.html",
    "/hxscar-website/services/bmw-premium.html",
    "/hxscar-website/services/air-conditioning.html",
    "/hxscar-website/services/chassis.html",
    "/hxscar-website/services/vehicle-restoration.html",
    "/hxscar-website/models/index.html",
}


def sitemap_urls():
    """读取站点地图中的 URL。"""
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [node.text for node in root.findall("sm:url/sm:loc", namespace)]


def selected_urls():
    """只提交与门店实体和服务搜索最相关的 URL。"""
    selected = []
    for url in sitemap_urls():
        path = urllib.parse.urlsplit(url).path
        if path in PRIORITY_PATHS or path.startswith(
            "/hxscar-website/answers/"
        ) or path.startswith(
            "/hxscar-website/cases/"
        ) or path.startswith(
            "/hxscar-website/services/"
        ) or path.startswith(
            "/hxscar-website/models/"
        ):
            selected.append(url)
    # 站点地图索引按规范只列出 sitemap.xml 和 image-sitemap.xml，
    # 自身不会被内容站点地图收录，因此在这里单独加入 IndexNow 请求。
    sitemap_index_url = f"https://{HOST}/hxscar-website/sitemap-index.xml"
    if sitemap_index_url not in selected:
        selected.append(sitemap_index_url)
    robots_url = f"https://{HOST}/hxscar-website/robots.txt"
    if robots_url not in selected:
        selected.append(robots_url)
    return selected


def wait_for_key(attempts=6, delay=10):
    """等待 GitHub Pages 发布验证文件。"""
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
                print(f"IndexNow 验证文件已上线，第 {attempt} 次检查通过")
                return True
        except OSError as exc:
            print(f"等待验证文件 {attempt}/{attempts}: {exc}")
        if attempt < attempts:
            time.sleep(delay)
    return False


def submit_payload(payload, endpoint):
    """优先用 curl 提交，规避系统 Python 的 LibreSSL 握手问题。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    result = subprocess.run(
        [
            "curl",
            "--http1.1",
            "--silent",
            "--show-error",
            "--max-time",
            "30",
            "--retry",
            "2",
            "--request",
            "POST",
            "--header",
            "Content-Type: application/json; charset=utf-8",
            "--header",
            "User-Agent: hxscar-indexnow/1.0",
            "--data-binary",
            "@-",
            "--output",
            "/dev/null",
            "--write-out",
            "%{http_code}",
            endpoint,
        ],
        input=body,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        status = int(result.stdout.decode("ascii", "ignore").strip() or "0")
        if 200 <= status < 300:
            return status
    error = result.stderr.decode("utf-8", "ignore").strip()

    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "hxscar-indexnow/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except OSError as exc:
        raise OSError(f"curl: {error or result.returncode}; Python: {exc}") from exc


def main():
    """提交 IndexNow 请求。"""
    parser = argparse.ArgumentParser(description="提交核心页面到 IndexNow")
    parser.add_argument("--dry-run", action="store_true", help="只打印请求，不发送")
    parser.add_argument("--wait", action="store_true", help="等待验证文件上线后再提交")
    args = parser.parse_args()

    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": selected_urls(),
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if args.wait and not wait_for_key():
        raise SystemExit("IndexNow 验证文件尚未上线，本次跳过")

    results = []
    for name, endpoint in ENDPOINTS:
        try:
            status = submit_payload(payload, endpoint)
        except OSError as exc:
            print(f"{name} 提交失败: {exc}")
            continue
        results.append((name, status))
        print(f"{name} HTTP {status}: {len(payload['urlList'])} 个 URL")
    if not results:
        raise SystemExit("所有 IndexNow 提交端点均失败")


if __name__ == "__main__":
    main()
