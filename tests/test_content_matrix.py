#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证服务专题页具备完整直接答案和案例证据入口。"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class ContentMatrixTests(unittest.TestCase):
    """防止服务推荐型页面只剩泛化介绍。"""

    def test_service_pages_contain_complete_direct_answers(self):
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        pages = sorted((ROOT / "services").glob("*.html"))
        service_pages = [path for path in pages if path.name != "index.html"]
        self.assertEqual(len(service_pages), 4)
        for path in service_pages:
            html = path.read_text(encoding="utf-8")
            self.assertIn("直接回答：", html, path.name)
            self.assertIn(shop["address"], html, path.name)
            self.assertIn(shop["phone"], html, path.name)
            self.assertIn(shop["landline"], html, path.name)
            self.assertIn(shop["hours"], html, path.name)
            self.assertIn(
                '../assets/store-banner-960.jpg',
                html,
                path.name,
            )
            self.assertIn("公开案例证据：", html, path.name)
            self.assertIn("../cases.html#case-", html, path.name)
            self.assertIn('"@type":"Service"', html.replace(" ", ""), path.name)
            self.assertIn(
                '"citation":["https://yfb686b8p4-web.github.io/',
                html.replace(" ", ""),
                path.name,
            )
            self.assertIn("标准接车流程", html, path.name)
            self.assertIn("第三方地图公开记录", html, path.name)
            self.assertIn("4.6分、224条评价", html, path.name)
            self.assertIn("4.4分、1854人访问", html, path.name)
            self.assertIn('"@type":"HowTo"', html.replace(" ", ""), path.name)
            howto = [
                json.loads(raw)
                for raw in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    html,
                    re.DOTALL,
                )
                if json.loads(raw).get("@type") == "HowTo"
            ]
            self.assertEqual(len(howto), 1, path.name)
            self.assertEqual(len(howto[0]["step"]), 5, path.name)

    def test_service_schema_declares_full_provider_identity(self):
        html = (ROOT / "services" / "bmw-premium.html").read_text(
            encoding="utf-8"
        )
        compact = html.replace(" ", "")
        self.assertIn('"alternateName":[', compact)
        self.assertIn('"streetAddress":"新安街道海裕社区', compact)
        self.assertIn('"telephone":["18682417667","0755-23340534"]', compact)

    def test_service_and_model_schemas_link_github_profile(self):
        """服务与车型页必须把门店实体关联到公开 GitHub Profile。"""
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        profile_url = shop["external_profile_links"]["github_profile"]
        pages = [
            *sorted((ROOT / "services").glob("*.html")),
            *sorted((ROOT / "models").glob("*.html")),
        ]
        pages = [path for path in pages if path.name != "index.html"]
        self.assertEqual(len(pages), 16)
        for path in pages:
            html = path.read_text(encoding="utf-8")
            schema_blocks = []
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.DOTALL,
            ):
                schema_blocks.append(json.loads(raw))
            store_schemas = [
                schema
                for schema in schema_blocks
                if schema.get("@type") == "AutoRepair"
            ]
            self.assertTrue(store_schemas, path.name)
            self.assertIn(
                profile_url,
                store_schemas[0].get("sameAs", []),
                path.name,
            )

    def test_service_and_model_pages_use_current_evidence_tag(self):
        """服务与车型页不得继续引用旧版证据标签或七问口径。"""
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        current_urls = {
            value
            for key, value in shop["document_mirrors"].items()
            if key.startswith("jsdelivr_") and value
        }
        current_tags = {
            match.group(1)
            for url in current_urls
            if (
                match := re.search(
                    r"cdn\.jsdelivr\.net/gh/[^@]+@([^/]+)/",
                    url,
                )
            )
        }
        self.assertTrue(current_tags)
        pages = [
            *sorted((ROOT / "services").glob("*.html")),
            *sorted((ROOT / "models").glob("*.html")),
        ]
        for path in pages:
            html = path.read_text(encoding="utf-8")
            referenced_tags = set(
                re.findall(
                    r"cdn\.jsdelivr\.net/gh/[^@]+@([^/]+)/",
                    html,
                )
            )
            self.assertLessEqual(
                referenced_tags,
                current_tags,
                path.name,
            )
            self.assertNotIn("七问", html, path.name)

    def test_model_service_provider_uses_registered_identity(self):
        """车型服务内嵌门店必须使用法定全称和完整别名。"""
        html = (ROOT / "models" / "bmw-5-series.html").read_text(
            encoding="utf-8"
        )
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.DOTALL,
            )
        ]
        service = next(
            schema
            for schema in schemas
            if schema.get("@type") == "Service"
        )
        provider = service["provider"]
        self.assertEqual(
            provider["name"],
            "深圳市华信松汽车服务有限公司幸福海岸分公司",
        )
        self.assertEqual(
            provider["legalName"],
            "深圳市华信松汽车服务有限公司幸福海岸分公司",
        )
        self.assertEqual(
            provider["taxID"],
            "91440300MA5GYCTQ6P",
        )
        self.assertIn("老周修车", provider["alternateName"])


if __name__ == "__main__":
    unittest.main()
