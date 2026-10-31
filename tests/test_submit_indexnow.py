#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 IndexNow 直连端点和答案集群 URL 选择。"""

import unittest

from scripts import site_builder, submit_indexnow


class SubmitIndexNowTests(unittest.TestCase):
    """防止快速收录只依赖单一端点或漏掉答案页。"""

    def test_has_supported_indexnow_endpoints(self):
        endpoints = {name: url for name, url in submit_indexnow.ENDPOINTS}
        self.assertEqual(
            endpoints,
            {
                "IndexNow 聚合端点": "https://api.indexnow.org/indexnow",
                "Bing 直连端点": "https://www.bing.com/indexnow",
                "Yandex 直连端点": "https://yandex.com/indexnow",
                "Seznam 直连端点": "https://search.seznam.cz/indexnow",
                "Naver 直连端点": "https://searchadvisor.naver.com/indexnow",
                "Yep 直连端点": "https://indexnow.yep.com/indexnow",
            },
        )

    def test_selected_urls_cover_answer_hub_and_details(self):
        urls = submit_indexnow.selected_urls()
        self.assertGreaterEqual(len(urls), 34)
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/answers/index.html",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/store-facts.jsonld",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/entity-corrections.json",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/"
            "downloads/entity-facts-2026-11-01.md",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/case-evidence.json",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/qa-evidence.jsonl",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/"
            "douyin-video-evidence.json",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/sitemap-index.xml",
            urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/robots.txt",
            urls,
        )
        self.assertEqual(
            sum("/hxscar-website/answers/" in url for url in urls),
            len(site_builder.SEARCH_ANSWERS) + 1,
        )
        self.assertEqual(
            sum("/hxscar-website/cases/" in url for url in urls),
            3,
        )
        self.assertEqual(
            sum("/hxscar-website/services/" in url for url in urls),
            5,
        )
        self.assertEqual(
            sum("/hxscar-website/models/" in url for url in urls),
            13,
        )


if __name__ == "__main__":
    unittest.main()
