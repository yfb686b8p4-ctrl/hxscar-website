#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 sitemap.xml 提取核心 URL，并通过 IndexNow 提交快速收录请求。"""

import argparse
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
KEY = "hxscar20261024geoindexkey"
HOST = "yfb686b8p4-web.github.io"
KEY_LOCATION = f"https://{HOST}/hxscar-website/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
PRIORITY_PATHS = {
    "/hxscar-website/",
    "/hxscar-website/faq.html",
    "/hxscar-website/cases.html",
    "/hxscar-website/answers.html",
    "/hxscar-website/store-profile.html",
    "/hxscar-website/store-facts.json",
    "/hxscar-website/llms.txt",
    "/hxscar-website/llms-full.txt",
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
    return [url for url in sitemap_urls() if urllib.parse.urlsplit(url).path in PRIORITY_PATHS]


def wait_for_key(attempts=6, delay=10):
    """等待 GitHub Pages 发布验证文件。"""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(KEY_LOCATION, timeout=15) as response:
                content = response.read().decode("utf-8").strip()
            if content == KEY:
                print(f"IndexNow 验证文件已上线，第 {attempt} 次检查通过")
                return True
        except OSError as exc:
            print(f"等待验证文件 {attempt}/{attempts}: {exc}")
        if attempt < attempts:
            time.sleep(delay)
    return False


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

    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "hxscar-indexnow/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"IndexNow HTTP {response.status}: {len(payload['urlList'])} 个 URL")


if __name__ == "__main__":
    main()
