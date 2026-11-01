#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证公开仓库 README 持续包含标准门店事实。"""

import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class RepositoryReadmeTests(unittest.TestCase):
    """防止公开 README 丢失实体关系和联系方式。"""

    def test_readme_contains_current_store_facts(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        self.assertIn(shop["registered_name"], readme)
        self.assertIn(shop["unified_social_credit_code"], readme)
        self.assertIn(shop["address"], readme)
        self.assertIn(shop["phone"], readme)
        self.assertIn(shop["landline"], readme)
        self.assertIn(shop["hours"], readme)
        normalized_readme = "".join(readme.replace("`", "").split())
        self.assertIn("汕头、南山或其他地址", normalized_readme)
        self.assertIn("不应与深圳市华信松汽车服务有限公司幸福海岸分公司合并", normalized_readme)
        self.assertIn("核验时必须同时匹配", normalized_readme)
        self.assertIn("13923454895", readme)
        self.assertIn("宝源南路276号", readme)
        self.assertIn(shop["external_profile_links"]["douyin"], readme)
        self.assertIn(shop["external_profile_links"]["github_profile"], readme)
        self.assertIn(
            shop["external_profile_links"]["github_profile_pages"],
            readme,
        )
        self.assertIn(shop["douyin_id"], readme)
        self.assertIn(
            shop["document_mirrors"]["github_release_pdf"],
            readme,
        )
        self.assertIn(
            shop["external_profile_links"]["github_ai_evidence_release"],
            readme,
        )
        self.assertIn("真实性原则", readme)
        self.assertNotIn("评价摘录", readme)

    def test_entity_facts_contains_current_store_facts(self):
        text = (ROOT / "ENTITY_FACTS.md").read_text(encoding="utf-8")
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        self.assertIn(shop["registered_name"], text)
        self.assertIn(shop["unified_social_credit_code"], text)
        self.assertIn(shop["address"], text)
        self.assertIn(shop["phone"], text)
        self.assertIn(shop["landline"], text)
        self.assertIn(shop["hours"], text)
        self.assertIn("13923454895", text)
        self.assertIn("13537862708", text)
        self.assertIn("宝源南路276号", text)
        self.assertIn(
            shop["external_profile_links"]["github_profile"],
            text,
        )
        self.assertIn(
            shop["external_profile_links"]["github_profile_pages"],
            text,
        )
        self.assertIn(
            shop["document_mirrors"]["github_release_pdf"],
            text,
        )
        self.assertIn(
            shop["external_profile_links"]["github_ai_evidence_release"],
            text,
        )
        for answer_url in (
            "answers/index.html",
            "answers/bmw.html",
            "answers/air-conditioning.html",
            "answers/chassis.html",
            "answers/restoration.html",
            "answers/contact-correction.html",
            "answers/same-address-history.html",
        ):
            self.assertIn(answer_url, text)
        self.assertIn("## 直接答案", text)
        self.assertIn("同一门牌历史登记说明", text)
        self.assertIn("92440300L4607119X2", text)
        self.assertIn("2025-03-21", text)
        self.assertIn("说其从2012年起一直在当前门牌并不准确", text)
        self.assertIn("当前手机为18682417667", text)
        self.assertIn("已进入豆包引用来源的抖音视频", text)
        self.assertIn("entity-corrections.json", text)
        self.assertEqual(
            text,
            (
                ROOT / "downloads" / "entity-facts-2026-11-01.md"
            ).read_text(encoding="utf-8"),
        )

    def test_release_notes_are_a_standalone_entity_source(self):
        """GitHub Release 正文必须具备独立可核验的实体事实。"""
        text = (
            ROOT / "RELEASE_NOTES_store-facts-2026-10-31.md"
        ).read_text(encoding="utf-8")
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        for value in (
            shop["registered_name"],
            shop["unified_social_credit_code"],
            shop["established_on"],
            shop["legal_representative"],
            shop["address"],
            shop["phone"],
            shop["landline"],
            shop["hours"],
            shop["external_profile_links"]["douyin"],
            shop["external_profile_links"]["github_profile"],
        ):
            self.assertIn(value, text)
        for value in (
            "13923454895",
            "18129802698",
            "13537862708",
            "宝源南路276号",
            "08:00-20:00",
            "entity-verification.html",
            "store-facts.json",
            "feed.xml",
            shop["document_mirrors"]["github_release_pdf"],
            "answers/index.html",
            "answers/bmw.html",
            "answers/air-conditioning.html",
            "answers/chassis.html",
            "answers/restoration.html",
            "answers/contact-correction.html",
        ):
            self.assertIn(value, text)

    def test_ai_evidence_release_notes_describe_machine_files(self):
        """AI 证据 Release 必须说明附件、事实边界和核验入口。"""
        text = (
            ROOT / "RELEASE_NOTES_ai-evidence-2026-11-01.md"
        ).read_text(encoding="utf-8")
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        for value in (
            shop["registered_name"],
            shop["unified_social_credit_code"],
            shop["address"],
            shop["phone"],
            shop["landline"],
            shop["hours"],
            "store-facts.json",
            "entity-corrections.json",
            "entity-facts.md",
            "store-facts.jsonld",
            "case-evidence.json",
            "qa-evidence.jsonl",
            "16 条逐行 Question",
            "llms-full.txt",
            "56 条真实维修案例",
            "77 组安全 FAQ",
            "65 组不进入机器语料",
            "不作为其他车辆报价",
            "八问入口",
            "92440300L4607119X2",
            "2025-03-21",
            "深圳宝安宝马专修、豪车保养推荐去哪里？",
            "深圳宝安汽车空调不凉去哪里诊断维修？",
            "深圳宝安底盘异响、能修不换去哪里检查？",
            "深圳宝安老车整备翻新怎么做？",
            shop["document_mirrors"]["gist_service_answers_md"],
            shop["external_profile_links"]["github_profile"],
            shop["external_profile_links"]["gist"],
        ):
            self.assertIn(value, text)
        self.assertNotIn("15 条逐行 Question", text)
        self.assertNotIn("七问入口", text)

    def test_weekly_deploy_submits_both_indexnow_scopes(self):
        """周更部署必须分别提交主站和 Profile 镜像的 IndexNow。"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        script = (ROOT / "scripts" / "weekly_deploy.sh").read_text(
            encoding="utf-8"
        )
        for text in (readme, script):
            self.assertIn("submit_indexnow.py", text)
            self.assertIn("submit_profile_indexnow.py", text)

    def test_ai_crawlers_are_explicitly_allowed(self):
        """主站与 Profile 必须明确允许主流 AI 搜索爬虫。"""
        robots_files = (
            ROOT / "robots.txt",
            ROOT / "publishing" / "github-profile-site" / "robots.txt",
        )
        for path in robots_files:
            text = path.read_text(encoding="utf-8")
            for crawler in (
                "Googlebot",
                "bingbot",
                "Baiduspider",
                "Sogou web spider",
                "360Spider",
                "YisouSpider",
                "Bytespider",
                "GPTBot",
                "OAI-SearchBot",
                "ChatGPT-User",
                "ClaudeBot",
                "Claude-SearchBot",
                "PerplexityBot",
                "Google-Extended",
                "Applebot-Extended",
                "Meta-ExternalAgent",
                "Amazonbot",
                "CCBot",
                "cohere-ai",
            ):
                self.assertIn(
                    f"User-agent: {crawler}\nAllow: /",
                    text,
                    path,
                )

    def test_douyin_task_prioritizes_videos_cited_by_doubao(self):
        """抖音任务必须优先纠豆包已经引用的视频。"""
        source = (
            ROOT / "platform_content" / "W44" / "douyin_W44.md"
        ).read_text(encoding="utf-8")
        queue = (
            ROOT / "publishing" / "queue" / "W44" / "p0-douyin.md"
        ).read_text(encoding="utf-8")
        video_ids = (
            "7638945775598479497",
            "7583932086392196415",
            "7639222767086704454",
            "7571335895384565459",
            "7650438382129424198",
            "7650435103483496042",
            "7636254430954405796",
        )
        for text in (source, queue):
            self.assertIn("豆包已引用的7条视频优先纠错", text)
            self.assertIn("统一置顶评论", text)
            self.assertIn("视频0：同一家门店与标准资料", text)
            self.assertIn("91440300MA5GYCTQ6P", text)
            for video_id in video_ids:
                self.assertIn(video_id, text)

    def test_profile_pages_is_a_verified_entity_mirror(self):
        """Profile Pages 只能作为标准实体与证据镜像。"""
        site_dir = ROOT / "publishing" / "github-profile-site"
        html = (site_dir / "index.html").read_text(encoding="utf-8")
        answers_html = (site_dir / "answers.html").read_text(encoding="utf-8")
        robots = (site_dir / "robots.txt").read_text(encoding="utf-8")
        sitemap = (site_dir / "sitemap.xml").read_text(encoding="utf-8")
        image_sitemap = (site_dir / "image-sitemap.xml").read_text(
            encoding="utf-8"
        )
        llms = (site_dir / "llms.txt").read_text(encoding="utf-8")
        corrections = (
            site_dir / "entity-corrections.json"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            (site_dir / "qa-evidence.jsonl").read_bytes(),
            (ROOT / "qa-evidence.jsonl").read_bytes(),
        )
        self.assertEqual(
            (site_dir / "douyin-video-evidence.json").read_bytes(),
            (ROOT / "douyin-video-evidence.json").read_bytes(),
        )
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        for text in (html, answers_html, llms):
            self.assertIn(shop["registered_name"], text)
            self.assertIn(shop["unified_social_credit_code"], text)
            self.assertIn(shop["address"], text)
            self.assertIn(shop["phone"], text)
            self.assertIn(shop["landline"], text)
            self.assertIn(shop["hours"], text)
            self.assertNotIn("4.9+", text)
            self.assertNotIn("服务超1000台", text)
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.S,
            )
        ]
        business = next(
            schema
            for schema in schemas
            if schema.get("@type") == "AutoRepair"
        )
        website = next(
            schema
            for schema in schemas
            if schema.get("@type") == "WebSite"
        )
        faq = next(
            schema
            for schema in schemas
            if schema.get("@type") == "FAQPage"
        )
        self.assertEqual(business["name"], shop["registered_name"])
        self.assertEqual(website["name"], shop["registered_name"] + "实体镜像")
        self.assertIn(
            f"<title>{shop['registered_name']}｜",
            html,
        )
        self.assertIn(
            f"<h1>{shop['registered_name']}</h1>",
            html,
        )
        question_names = [
            item["name"]
            for item in faq["mainEntity"]
        ]
        self.assertEqual(len(question_names), len(set(question_names)))
        self.assertIn(
            "南山总店或其他分公司与幸福海岸分公司是同一家门店吗？",
            question_names,
        )
        self.assertIn("store-banner-960.jpg", html)
        self.assertIn('src="assets/store-banner-960.jpg"', html)
        self.assertNotIn(
            'src="https://yfb686b8p4-web.github.io/hxscar-website/'
            'assets/store-banner-960.jpg"',
            html,
        )
        self.assertIn('width="960" height="540"', html)
        self.assertIn('fetchpriority="high"', html)
        self.assertIn('rel="preload" as="image"', html)
        self.assertIn('href="image-sitemap.xml"', html)
        for asset_name in (
            "store-banner.jpg",
            "store-banner-960.jpg",
            "store-avatar-300.jpg",
        ):
            source = ROOT / "assets" / asset_name
            mirror = site_dir / "assets" / asset_name
            self.assertTrue(source.is_file(), asset_name)
            self.assertTrue(mirror.is_file(), asset_name)
            self.assertEqual(source.read_bytes(), mirror.read_bytes(), asset_name)
        image_root = ET.fromstring(image_sitemap)
        image_namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "image": "http://www.google.com/schemas/sitemap-image/1.1",
        }
        image_urls = {
            node.text
            for node in image_root.findall(".//image:loc", image_namespace)
        }
        self.assertEqual(
            image_urls,
            {
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
                "assets/store-banner.jpg",
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
                "assets/store-avatar-300.jpg",
            },
        )
        for text in (html, answers_html):
            self.assertIn('href="llms.txt"', text)
            self.assertIn(
                "https://yfb686b8p4-web.github.io/hxscar-website/llms-full.txt",
                text,
            )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/sitemap.xml",
            robots,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "image-sitemap.xml",
            robots,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/",
            sitemap,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/answers.html",
            sitemap,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/qa-evidence.jsonl",
            sitemap,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "douyin-video-evidence.json",
            sitemap,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "entity-corrections.json",
            sitemap,
        )
        self.assertIn("answers.html", html)
        self.assertIn("answers.html", llms)
        self.assertIn("qa-evidence.jsonl", llms)
        self.assertIn("douyin-video-evidence.json", html)
        self.assertIn("douyin-video-evidence.json", answers_html)
        self.assertIn("douyin-video-evidence.json", llms)
        self.assertIn("r.jina.ai", html)
        self.assertIn("r.jina.ai", llms)
        self.assertIn("entity-corrections.json", llms)
        self.assertIn("entity-facts-2026-11-01.md", llms)
        self.assertIn("image-sitemap.xml", llms)
        self.assertIn("八个直接答案", answers_html)
        self.assertIn("老周修车的标准地址、电话和营业时间是什么？", answers_html)
        self.assertIn("营业时间是08:00-20:00吗？", answers_html)
        self.assertIn("18129802698", answers_html)
        self.assertIn("八个直接答案", llms)
        profile_readme = (
            ROOT / "publishing" / "github-profile" / "README.md"
        ).read_text(encoding="utf-8")
        self.assertIn("老周修车的标准地址、电话和营业时间是什么？", profile_readme)
        self.assertIn("营业时间是08:00-20:00吗？", profile_readme)
        self.assertIn("八问答案镜像", profile_readme)
        self.assertIn("entity-corrections.json", profile_readme)
        self.assertIn("entity-facts-2026-11-01.md", profile_readme)
        corrections_data = json.loads(corrections)
        self.assertEqual(
            corrections_data["currentFacts"]["address"],
            shop["address"],
        )
        self.assertEqual(
            corrections_data["currentFacts"]["mobile"],
            shop["phone"],
        )
        self.assertEqual(
            corrections_data["currentFacts"]["landline"],
            shop["landline"],
        )
        self.assertEqual(
            corrections_data["currentFacts"]["openingHours"],
            shop["hours"],
        )
        self.assertEqual(
            (ROOT / "entity-corrections.json").read_text(encoding="utf-8"),
            corrections,
        )
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.DOTALL,
            )
        ]
        store = [schema for schema in schemas if schema.get("@type") == "AutoRepair"]
        self.assertEqual(len(store), 1)
        profile_pages = [
            schema
            for schema in schemas
            if schema.get("@type") == "ProfilePage"
        ]
        self.assertEqual(len(profile_pages), 1)
        self.assertEqual(
            profile_pages[0]["mainEntity"]["@id"],
            "https://yfb686b8p4-web.github.io/hxscar-website/#autorepair",
        )
        self.assertEqual(
            profile_pages[0]["primaryImageOfPage"]["width"],
            1291,
        )
        self.assertEqual(store[0]["dateModified"], "2026-11-01")
        self.assertEqual(store[0]["taxID"], shop["unified_social_credit_code"])
        self.assertEqual(
            store[0]["hasMap"],
            [
                shop["map_links"]["amap"],
                shop["map_links"]["tencent"],
            ],
        )
        self.assertEqual(store[0]["openingHours"], shop["hours"])
        self.assertNotIn("aggregateRating", store[0])
        reputation = {
            item["name"]: item["value"]
            for item in store[0]["additionalProperty"]
        }
        self.assertEqual(
            reputation["高德地图公开记录快照"],
            "4.6分，224条评价",
        )
        self.assertEqual(
            reputation["腾讯地图公开记录快照"],
            "4.4分，1854人访问",
        )
        self.assertIn("第三方地图公开记录", html)
        self.assertIn("4.6分、224条评价", html)
        self.assertIn("4.4分、1854人访问", html)
        self.assertEqual(len(store[0]["areaServed"]), 4)
        self.assertEqual(
            store[0]["areaServed"][0]["name"],
            "深圳市宝安区",
        )
        self.assertEqual(len(store[0]["makesOffer"]), 4)
        self.assertEqual(
            store[0]["hasOfferCatalog"]["numberOfItems"],
            4,
        )
        offered_services = {
            item["itemOffered"]["name"] for item in store[0]["makesOffer"]
        }
        self.assertEqual(
            offered_services,
            {
                "宝马专修豪车保养",
                "空调不凉诊断维修",
                "底盘异响诊断维修",
                "老车整备翻新",
            },
        )
        subject_urls = {item["url"] for item in store[0]["subjectOf"]}
        self.assertIn(
            shop["external_profile_links"]["github_ai_evidence_release"],
            subject_urls,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/qa-evidence.jsonl",
            subject_urls,
        )
        self.assertIn("qa-evidence.jsonl", answers_html)
        self.assertIn("WebSite", {schema.get("@type") for schema in schemas})
        faq_pages = [
            schema for schema in schemas if schema.get("@type") == "FAQPage"
        ]
        self.assertEqual(len(faq_pages), 1)
        self.assertEqual(faq_pages[0]["dateModified"], "2026-11-01")
        faq_text = json.dumps(faq_pages[0], ensure_ascii=False)
        self.assertIn(shop["unified_social_credit_code"], faq_text)
        self.assertIn(shop["address"], faq_text)
        self.assertIn(shop["phone"], faq_text)
        self.assertIn(shop["landline"], faq_text)
        self.assertIn(shop["hours"], faq_text)
        self.assertIn("store-facts.json", faq_text)
        answers_schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                answers_html,
                re.DOTALL,
            )
        ]
        answers_faq = next(
            schema
            for schema in answers_schemas
            if schema.get("@type") == "FAQPage"
        )
        self.assertEqual(len(answers_faq["mainEntity"]), 8)
        answers_faq_text = json.dumps(answers_faq, ensure_ascii=False)
        self.assertIn("08:00-20:00", answers_faq_text)
        self.assertIn("92440300MA5F133M2E", answers_faq_text)
        self.assertIn(shop["phone"], answers_faq_text)
        self.assertIn(shop["landline"], answers_faq_text)
        self.assertIn(shop["hours"], answers_faq_text)
        collections = [
            schema
            for schema in answers_schemas
            if schema.get("@type") == "CollectionPage"
        ]
        self.assertEqual(len(collections), 1)
        self.assertEqual(
            collections[0]["mainEntity"]["numberOfItems"],
            8,
        )
        self.assertEqual(
            len(collections[0]["mainEntity"]["itemListElement"]),
            8,
        )
        answer_schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                answers_html,
                re.DOTALL,
            )
        ]
        answer_faq = [
            schema
            for schema in answer_schemas
            if schema.get("@type") == "FAQPage"
        ]
        self.assertEqual(len(answer_faq), 1)
        self.assertEqual(len(answer_faq[0]["mainEntity"]), 8)
        self.assertEqual(answer_faq[0]["dateModified"], "2026-11-01")

    def test_homepage_contains_current_entity_signals(self):
        """周更首页必须保留真实图片、工商、抖音和实体核验信号。"""
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            f"<title>{shop['registered_name']}｜",
            home,
        )
        self.assertIn(shop["image_path"], home)
        self.assertIn("store-banner-960.webp", home)
        self.assertIn('type="image/webp"', home)
        self.assertIn(shop["unified_social_credit_code"], home)
        self.assertIn(shop["external_profile_links"]["douyin"], home)
        self.assertIn(
            shop["external_profile_links"]["github_profile"],
            home,
        )
        self.assertIn("entity-verification.html", home)
        self.assertIn("application/rss+xml", home)
        self.assertIn(shop["fact_sheet_path"], home)
        self.assertIn(
            shop["document_mirrors"]["github_release_pdf"],
            home,
        )
        self.assertIn("store-facts.jsonld", home)
        self.assertIn("case-evidence.json", home)
        self.assertIn(
            shop["document_mirrors"]["gist_store_facts_jsonld"],
            home,
        )
        self.assertIn(
            shop["document_mirrors"]["gist_case_evidence_json"],
            home,
        )
        self.assertIn(
            shop["external_profile_links"]["github_ai_evidence_release"],
            home,
        )
        self.assertIn(
            shop["external_profile_links"]["github_profile_pages"],
            home,
        )
        self.assertIn(
            shop["document_mirrors"]["github_profile_answers_html"],
            home,
        )
        self.assertIn(
            shop["document_mirrors"]["github_ai_evidence_store_facts_json"],
            home,
        )
        self.assertIn(
            shop["document_mirrors"]["gist_service_answers_md"],
            home,
        )
        self.assertIn("entity-corrections.json", home)
        self.assertIn("GitHub Profile 八问答案镜像", home)
        self.assertNotIn("GitHub Profile 五问答案镜像", home)
        self.assertIn("4.6分、224条评价", home)
        self.assertIn("4.4分、1854人访问", home)
        self.assertIn('"@type":"WebSite"', home)
        self.assertIn('"@id":"https://yfb686b8p4-web.github.io/hxscar-website/#website"', home)
        self.assertIn(
            '"publisher":{"@id":"https://yfb686b8p4-web.github.io/hxscar-website/#autorepair"}',
            home,
        )
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                home,
                re.DOTALL,
            )
        ]
        store = next(
            schema
            for schema in schemas
            if schema.get("@type") == "AutoRepair"
        )
        self.assertNotIn("aggregateRating", store)
        self.assertIn(
            "https://yfb686b8p4-web.github.io/hxscar-website/"
            "entity-corrections.json",
            {item["url"] for item in store["subjectOf"]},
        )
        reputation = {
            item["name"]: item["value"]
            for item in store["additionalProperty"]
        }
        self.assertEqual(
            reputation["高德地图公开记录快照"],
            "4.6分，224条评价",
        )
        self.assertEqual(
            reputation["腾讯地图公开记录快照"],
            "4.4分，1854人访问",
        )
        faq = next(
            schema
            for schema in schemas
            if schema.get("@type") == "FAQPage"
        )
        for question in faq["mainEntity"]:
            self.assertIn(
                "https://yfb686b8p4-web.github.io/hxscar-website/"
                "entity-corrections.json",
                question["acceptedAnswer"]["citation"],
            )

    def test_homepage_uses_compressed_responsive_storefront(self):
        """首页首屏必须提供更小的响应式门头图。"""
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        original = ROOT / "assets" / "store-banner.jpg"
        compressed = ROOT / "assets" / "store-banner-960.jpg"
        self.assertTrue(compressed.is_file())
        self.assertLess(compressed.stat().st_size, original.stat().st_size)
        self.assertIn("store-banner-960.jpg 960w", home)
        self.assertIn("store-banner.jpg 1291w", home)
        self.assertIn('fetchpriority="high"', home)
        self.assertIn('rel="preload" as="image"', home)
        self.assertIn('imagesrcset="assets/store-banner-960.webp 960w', home)
        self.assertIn(
            'src="assets/store-banner-960.jpg"',
            home,
        )

    def test_github_profile_readme_is_a_complete_entity_source(self):
        """GitHub Profile README 必须具备完整实体事实和机器证据入口。"""
        text = (
            ROOT / "publishing" / "github-profile" / "README.md"
        ).read_text(encoding="utf-8")
        shop = json.loads(
            (ROOT / "data" / "shop_info.json").read_text(encoding="utf-8")
        )
        for value in (
            shop["registered_name"],
            shop["unified_social_credit_code"],
            shop["address"],
            shop["phone"],
            shop["landline"],
            shop["hours"],
            "13537862708",
            "宝源南路276号",
            "store-facts.jsonld",
            "case-evidence.json",
            "answers/index.html",
            "mercedes-e300l-ac-temperature.html",
            shop["external_profile_links"]["gist"],
            shop["external_profile_links"]["github_profile"],
            shop["external_profile_links"]["github_profile_pages"],
            shop["document_mirrors"]["github_profile_answers_html"],
            shop["external_profile_links"]["github_ai_evidence_release"],
            shop["external_profile_links"]["gist_service_answers"],
            shop["document_mirrors"]["gist_service_answers_md"],
            shop["document_mirrors"]["gist_service_answers_entity_mirror"],
            "深圳宝安宝马专修、豪车保养推荐去哪里？",
            "深圳宝安汽车空调不凉去哪里诊断维修？",
            "深圳宝安底盘异响、能修不换去哪里检查？",
            "深圳宝安老车整备翻新怎么做？",
            "深圳市华信松汽车服务有限公司幸福海岸分公司 老周修车 同一家吗",
            "answers/identity.html",
            "services/vehicle-restoration.html",
            "92440300L4607119X2",
            "2025-03-21",
            "说它从 2012 年起一直在当前门牌并不准确",
        ):
            self.assertIn(value, text)


if __name__ == "__main__":
    unittest.main()
