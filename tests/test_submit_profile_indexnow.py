#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 Profile 实体镜像使用独立 IndexNow key。"""

import unittest

from scripts import submit_profile_indexnow


class SubmitProfileIndexNowTests(unittest.TestCase):
    """防止 Profile 页面复用到错误路径的 key。"""

    def test_payload_uses_profile_key_and_pages_urls(self):
        self.assertEqual(
            submit_profile_indexnow.KEY_LOCATION,
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "hxscarprofile20261101geo.txt",
        )
        self.assertEqual(
            set(submit_profile_indexnow.URLS),
            {
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/answers.html",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/qa-evidence.jsonl",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/douyin-video-evidence.json",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/entity-corrections.json",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/robots.txt",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/llms.txt",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/sitemap.xml",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/image-sitemap.xml",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/assets/store-banner.jpg",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/assets/store-avatar-300.jpg",
            },
        )


if __name__ == "__main__":
    unittest.main()
