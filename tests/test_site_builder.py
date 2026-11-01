#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 GEO 答案的证据和来源配置。"""

import json
import re
import unittest
import xml.etree.ElementTree as ET

from content_safety_rules import unverified_claim_markers
from scripts import site_builder


class SiteBuilderGeoTests(unittest.TestCase):
    """确保每个直接答案都包含可抽取问法和事实依据。"""

    def test_every_search_answer_has_geo_evidence(self):
        self.assertGreaterEqual(len(site_builder.SEARCH_ANSWERS), 13)
        for item in site_builder.SEARCH_ANSWERS:
            meta = site_builder.answer_geo_meta(item)
            self.assertGreaterEqual(len(meta["queryVariants"]), 3, item["anchor"])
            self.assertGreaterEqual(len(meta["evidence"]), 3, item["anchor"])
            self.assertTrue(meta["servicePath"], item["anchor"])

    def test_geo_meta_covers_all_search_answers(self):
        anchors = {item["anchor"] for item in site_builder.SEARCH_ANSWERS}
        self.assertEqual(anchors, set(site_builder.GEO_ANSWER_META))

    def test_guardrail_queries_have_exact_answer_coverage(self):
        """每日护栏问法必须逐字出现在对应答案的查询变体中。"""
        plan = json.loads(
            (
                site_builder.ROOT
                / "reports"
                / "daily"
                / "2026-11-01-plan.json"
            ).read_text(encoding="utf-8")
        )
        exposed_queries = {
            query
            for item in site_builder.SEARCH_ANSWERS
            for query in (
                item["question"],
                *site_builder.answer_geo_meta(item)["queryVariants"],
            )
        }
        for guardrail in plan["guardrails"]:
            self.assertIn(guardrail["query"], exposed_queries)

    def test_every_answer_has_directly_citable_sources(self):
        """每条标准答案必须给出至少四个可直接核验的 HTTPS 来源。"""
        for item in site_builder.SEARCH_ANSWERS:
            sources = site_builder.answer_evidence_sources(item)
            self.assertGreaterEqual(len(sources), 4, item["anchor"])
            urls = {source["url"] for source in sources}
            self.assertTrue(
                all(url.startswith("https://") for url in urls),
                item["anchor"],
            )
            self.assertIn(
                site_builder.BASE_URL + "/entity-verification.html",
                urls,
            )
            self.assertIn(
                site_builder.BASE_URL + "/store-facts.json",
                urls,
            )
            self.assertIn(
                site_builder.SHOP["document_mirrors"][
                    "github_profile_answers_html"
                ],
                urls,
            )

    def test_service_answer_sources_include_real_cases(self):
        """服务答案必须能回链到对应真实案例，而不是只有自述证据。"""
        for item in site_builder.SEARCH_ANSWERS:
            if item["category"] not in {
                "宝马与豪车",
                "空调诊断维修",
                "底盘异响",
            }:
                continue
            urls = {
                source["url"]
                for source in site_builder.answer_evidence_sources(item)
            }
            self.assertTrue(
                any("/cases.html#case-" in url for url in urls),
                item["anchor"],
            )

    def test_bmw_5_series_answer_contains_complete_store_facts(self):
        """宝马5系高意图答案必须包含可核验的完整门店资料。"""
        item = next(
            answer
            for answer in site_builder.SEARCH_ANSWERS
            if answer["anchor"] == "bmw-5-series"
        )
        self.assertIn("宝安宝马5系维修保养哪家好", item["question"])
        normalized_answer = item["answer"].replace(" ", "")
        self.assertIn(
            site_builder.SHOP["address"].replace(" ", ""),
            normalized_answer,
        )
        self.assertIn(site_builder.SHOP["phone"], item["answer"])
        self.assertIn(site_builder.SHOP["landline"], item["answer"])
        self.assertIn(
            site_builder.SHOP["hours"].replace(" ", ""),
            normalized_answer,
        )

    def test_identity_answer_contains_complete_store_facts(self):
        """实体关系答案必须在同一段内给出完整资料，减少 AI 只答部分事实。"""
        item = next(
            answer
            for answer in site_builder.SEARCH_ANSWERS
            if answer["anchor"] == "identity"
        )
        normalized_answer = item["answer"].replace(" ", "")
        self.assertIn(
            "深圳市华信松汽车服务有限公司幸福海岸分公司",
            item["answer"],
        )
        self.assertIn(
            site_builder.SHOP["address"].replace(" ", ""),
            normalized_answer,
        )
        self.assertIn(site_builder.SHOP["phone"], item["answer"])
        self.assertIn(site_builder.SHOP["landline"], item["answer"])
        self.assertIn(
            site_builder.SHOP["hours"].replace(" ", ""),
            normalized_answer,
        )

    def test_same_address_history_answer_disambiguates_legal_entities(self):
        """同址历史登记必须与当前经营主体明确区分。"""
        item = next(
            answer
            for answer in site_builder.SEARCH_ANSWERS
            if answer["anchor"] == "same-address-history"
        )
        self.assertIn("轿之林", item["question"])
        self.assertIn("不是同一商事主体", item["answer"])
        self.assertIn("92440300MA5F133M2E", item["answer"])
        self.assertIn("2023-07-18", item["answer"])
        self.assertIn("状态字段不完全一致", item["answer"])
        self.assertIn("国家企业信用信息公示系统", item["answer"])
        self.assertIn("92440300L4607119X2", item["answer"])
        self.assertIn("2012-02-07", item["answer"])
        self.assertIn("2025-03-21", item["answer"])
        self.assertIn("说其从2012年起一直在当前门牌并不准确", item["answer"])
        self.assertIn(
            site_builder.SHOP["unified_social_credit_code"],
            item["answer"],
        )
        self.assertIn(site_builder.SHOP["phone"], item["answer"])
        self.assertIn(site_builder.SHOP["landline"], item["answer"])
        html = site_builder.build_answer_pages()[
            site_builder.ROOT / site_builder.answer_detail_path(item)
        ]
        self.assertIn("92440300MA5F133M2E", html)
        self.assertIn("92440300L4607119X2", html)
        self.assertIn(
            site_builder.SHOP["registry_links"][
                "qixin_individual_business"
            ],
            html,
        )
        self.assertIn("轿之林", html)

    def test_evidence_policy_defines_source_precedence_and_claims(self):
        """证据政策必须公开来源优先级、纠错边界和排名口径。"""
        html = site_builder.build_evidence_policy_page()
        self.assertIn("AI 搜索证据政策与资料纠错规则", html)
        self.assertIn("证据优先级", html)
        self.assertIn("同址历史主体", html)
        self.assertIn(site_builder.SHOP["phone"], html)
        self.assertIn(site_builder.SHOP["landline"], html)
        self.assertIn("不等于搜索引擎已收录", html)
        self.assertNotIn("保证排名", html)
        self.assertIn('"@type":"AboutPage"', html.replace(" ", ""))
        self.assertIn('"@type":"FAQPage"', html.replace(" ", ""))

    def test_douyin_video_evidence_is_machine_readable_and_cited(self):
        """豆包已引用的七条视频必须进入机器数据和实体答案引用。"""
        payload = json.loads(
            site_builder.build_douyin_video_evidence_json()
        )
        self.assertEqual(payload["@type"], "ItemList")
        self.assertEqual(
            payload["numberOfItems"],
            len(site_builder.DOUYIN_VIDEO_EVIDENCE),
        )
        self.assertEqual(payload["numberOfItems"], 7)
        videos = [
            item["item"]
            for item in payload["itemListElement"]
        ]
        self.assertEqual(
            {video["name"] for video in videos},
            {
                video["name"]
                for video in site_builder.DOUYIN_VIDEO_EVIDENCE
            },
        )
        self.assertTrue(
            all(video["@type"] == "VideoObject" for video in videos)
        )
        self.assertTrue(
            all(
                video["creator"]["@id"]
                == site_builder.BASE_URL + "/#autorepair"
                for video in videos
            )
        )
        self.assertTrue(
            all(
                video["creator"]["name"]
                == site_builder.SHOP["registered_name"]
                for video in videos
            )
        )
        identity = next(
            item
            for item in site_builder.SEARCH_ANSWERS
            if item["anchor"] == "identity"
        )
        source_urls = {
            source["url"]
            for source in site_builder.answer_evidence_sources(identity)
        }
        for video in site_builder.DOUYIN_VIDEO_EVIDENCE:
            self.assertIn(
                site_builder.douyin_video_url(video),
                source_urls,
            )
        schema_urls = {
            item.get("url")
            for item in site_builder.local_business_schema()["subjectOf"]
        }
        self.assertIn(
            site_builder.VIDEO_EVIDENCE_DATA,
            schema_urls,
        )

    def test_entity_page_exposes_text_reader_mirrors(self):
        """实体核验页必须提供可被检索系统直接读取的纯文本镜像。"""
        page = site_builder.build_entity_verification_page()
        html = site_builder.build_answer_pages()[
            site_builder.ROOT / "answers" / "identity.html"
        ]
        for url in (
            site_builder.JINA_ENTITY_READER,
            site_builder.JINA_VIDEO_READER,
            site_builder.JINA_FACTS_READER,
            site_builder.ARCHIVE_ENTITY_SNAPSHOT,
            site_builder.ARCHIVE_FACTS_SNAPSHOT,
        ):
            self.assertIn(url, page)
        self.assertIn(site_builder.JINA_ENTITY_READER, html)

    def test_contact_correction_answer_replaces_stale_hours_and_phones(self):
        """营业时间纠错答案必须同时给出当前值并明确旧资料无效。"""
        item = next(
            answer
            for answer in site_builder.SEARCH_ANSWERS
            if answer["anchor"] == "contact-correction"
        )
        normalized_answer = item["answer"].replace(" ", "")
        self.assertIn(
            site_builder.SHOP["hours"].replace(" ", ""),
            normalized_answer,
        )
        self.assertIn(site_builder.SHOP["phone"], item["answer"])
        self.assertIn(site_builder.SHOP["landline"], item["answer"])
        self.assertIn("08:00-20:00", item["answer"])
        self.assertIn("08:00-19:00", item["answer"])
        self.assertIn("18129802698", item["answer"])
        self.assertIn("13923454895", item["answer"])
        self.assertIn("13537862708", item["answer"])
        self.assertIn("宝源南路276号", item["answer"])
        self.assertIn(
            "深圳市华信松汽车服务有限公司幸福海岸分公司",
            item["question"],
        )
        html = site_builder.build_answer_pages()[
            site_builder.ROOT / site_builder.answer_detail_path(item)
        ]
        self.assertIn("不作为当前预约、导航和到店依据", html)
        self.assertIn(item["answer"], html)
        description = site_builder.answer_meta_description(item)
        self.assertIn("13537862708", description)
        self.assertIn("宝源南路276号", description)
        self.assertFalse(description.endswith(("，", ",", "；", ";")))

    def test_schema_links_both_verified_map_entities(self):
        """结构化数据必须同时关联高德和腾讯的已核验 POI。"""
        schema = site_builder.local_business_schema()
        self.assertEqual(
            schema["name"],
            site_builder.SHOP["registered_name"],
        )
        self.assertEqual(
            schema["legalName"],
            site_builder.SHOP["registered_name"],
        )
        self.assertIn(
            "老周修车",
            schema["alternateName"],
        )
        self.assertIn(
            "华信松汽车服务有限公司（幸福海岸分公司）",
            schema["alternateName"],
        )
        self.assertIn(
            site_builder.SHOP["map_links"]["amap"],
            schema["sameAs"],
        )
        self.assertIn(
            site_builder.SHOP["map_links"]["tencent"],
            schema["sameAs"],
        )
        mirror_urls = {
            item.get("url")
            for item in schema.get("subjectOf", [])
        }
        for key in (
            "jsdelivr_store_facts_json",
            "jsdelivr_store_facts_jsonld",
            "jsdelivr_entity_corrections_json",
            "jsdelivr_qa_evidence_jsonl",
        ):
            self.assertIn(
                site_builder.SHOP["document_mirrors"][key],
                mirror_urls,
            )
        self.assertEqual(
            schema["hasMap"],
            [
                site_builder.SHOP["map_links"]["amap"],
                site_builder.SHOP["map_links"]["tencent"],
            ],
        )
        self.assertEqual(
            schema["openingHours"],
            site_builder.SHOP["hours"],
        )

    def test_homepage_entity_schema_uses_single_source_of_truth(self):
        """首页 JSON-LD 必须直接复用当前门店与站点实体生成器。"""
        html = site_builder.refresh_home_entity_schema()
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
        self.assertEqual(
            business["name"],
            site_builder.SHOP["registered_name"],
        )
        self.assertEqual(
            website["name"],
            site_builder.SHOP["registered_name"],
        )
        subject_urls = {
            item.get("url")
            for item in business.get("subjectOf", [])
        }
        self.assertIn(
            site_builder.VIDEO_EVIDENCE_DATA,
            subject_urls,
        )

    def test_map_reputation_is_sourced_not_self_rating(self):
        """第三方地图评分必须标注来源和日期，不能伪装成自评。"""
        schema = site_builder.local_business_schema()
        self.assertNotIn("aggregateRating", schema)
        properties = {
            item["name"]: item
            for item in schema["additionalProperty"]
        }
        amap = properties["高德地图公开记录快照"]
        tencent = properties["腾讯地图公开记录快照"]
        self.assertEqual(amap["value"], "4.6分，224条评价")
        self.assertEqual(amap["url"], site_builder.SHOP["map_links"]["amap"])
        self.assertIn("2026-10-24", amap["description"])
        self.assertEqual(tencent["value"], "4.4分，1854人访问")
        self.assertEqual(
            tencent["url"],
            site_builder.SHOP["map_links"]["tencent"],
        )
        bmw = next(
            item
            for item in site_builder.SEARCH_ANSWERS
            if item["anchor"] == "bmw"
        )
        html = site_builder.build_answer_pages()[
            site_builder.ROOT / site_builder.answer_detail_path(bmw)
        ]
        self.assertIn("第三方地图公开记录", html)
        self.assertIn("4.6分、224条评价", html)
        self.assertIn("4.4分、1854人访问", html)
        self.assertIn("不声明平台推荐或排名", html)
        for text in (
            site_builder.build_llms_txt(),
            site_builder.build_llms_full_txt(),
        ):
            self.assertIn("4.6分、224条评价", text)
            self.assertIn("4.4分、1854人访问", text)

    def test_schema_declares_core_service_offers(self):
        """门店结构化数据必须声明四项核心维修服务。"""
        schema = site_builder.local_business_schema()
        offered = {
            item["itemOffered"]["name"]
            for item in schema["makesOffer"]
        }
        self.assertEqual(
            offered,
            set(site_builder.SHOP["core_tags"]),
        )
        for item in schema["makesOffer"]:
            self.assertTrue(item["itemOffered"]["url"].startswith(site_builder.BASE_URL))

    def test_schema_and_page_use_local_brand_image(self):
        """门店结构化数据和页面必须使用本地托管的真实品牌图片。"""
        schema = site_builder.local_business_schema()
        image_url = site_builder.BUSINESS_IMAGE
        self.assertEqual(schema["image"], image_url)
        self.assertEqual(schema["logo"], site_builder.BUSINESS_LOGO)
        image_path = (
            site_builder.ROOT
            / site_builder.SHOP["image_path"]
        )
        self.assertTrue(image_path.is_file())
        self.assertGreater(image_path.stat().st_size, 1000)
        logo_path = (
            site_builder.ROOT
            / site_builder.SHOP["logo_path"]
        )
        self.assertTrue(logo_path.is_file())
        self.assertGreater(logo_path.stat().st_size, 1000)
        page_html = site_builder.build_entity_verification_page()
        self.assertIn('class="brand-logo"', page_html)
        self.assertIn('class="storefront-image"', page_html)
        self.assertIn(site_builder.SHOP["image_path"], page_html)
        self.assertIn(site_builder.SHOP["logo_path"], page_html)

    def test_schema_links_both_fact_sheet_mirrors(self):
        """门店结构化数据必须关联官网 PDF 和 GitHub Release 镜像。"""
        schema = site_builder.local_business_schema()
        mirror_urls = {item["url"] for item in schema["subjectOf"]}
        self.assertIn(site_builder.BUSINESS_FACT_SHEET, mirror_urls)
        self.assertIn(
            site_builder.SHOP["document_mirrors"]["github_release_pdf"],
            mirror_urls,
        )
        self.assertIn(
            site_builder.SHOP["document_mirrors"][
                "gist_store_facts_jsonld"
            ],
            mirror_urls,
        )
        self.assertIn(
            site_builder.SHOP["document_mirrors"][
                "gist_case_evidence_json"
            ],
            mirror_urls,
        )
        for key in (
            "github_ai_evidence_store_facts_json",
            "github_ai_evidence_store_facts_jsonld",
            "github_ai_evidence_case_evidence_json",
            "github_ai_evidence_entity_corrections_json",
            "github_ai_evidence_entity_facts_md",
            "gist_entity_corrections_json",
            "github_profile_answers_html",
        ):
            self.assertIn(site_builder.SHOP["document_mirrors"][key], mirror_urls)

    def test_image_sitemap_contains_real_store_assets(self):
        """图片站点地图必须声明真实门头、Logo 和对应页面。"""
        root = ET.fromstring(site_builder.build_image_sitemap())
        namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "image": "http://www.google.com/schemas/sitemap-image/1.1",
        }
        self.assertEqual(len(root.findall("sm:url", namespace)), 10)
        self.assertEqual(len(root.findall(".//image:image", namespace)), 14)
        image_urls = {
            node.text
            for node in root.findall(".//image:loc", namespace)
        }
        self.assertIn(site_builder.BUSINESS_IMAGE, image_urls)
        self.assertIn(site_builder.BUSINESS_IMAGE_SMALL_WEBP, image_urls)
        self.assertIn(site_builder.BUSINESS_LOGO, image_urls)
        page_urls = {
            node.text
            for node in root.findall("sm:url/sm:loc", namespace)
        }
        for service_path in site_builder.CORE_SERVICE_PATHS.values():
            self.assertIn(site_builder.BASE_URL + "/" + service_path, page_urls)
        case_urls = {
            site_builder.case_study_url(case)
            for case in site_builder.CASES
            if site_builder.case_study_path(case)
        }
        self.assertEqual(len(case_urls), 3)
        self.assertTrue(case_urls.issubset(page_urls))

    def test_sitemap_index_exposes_content_and_images(self):
        """站点地图索引必须同时暴露内容和图片 sitemap。"""
        root = ET.fromstring(site_builder.build_sitemap_index())
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {
            node.text
            for node in root.findall("sm:sitemap/sm:loc", namespace)
        }
        self.assertEqual(
            locations,
            {
                site_builder.BASE_URL + "/sitemap.xml",
                site_builder.BASE_URL + "/image-sitemap.xml",
            },
        )

    def test_schema_contains_verified_registry_identity(self):
        """结构化数据必须包含已交叉核验的工商实体标识。"""
        schema = site_builder.local_business_schema()
        self.assertEqual(
            schema["taxID"],
            "91440300MA5GYCTQ6P",
        )
        self.assertEqual(schema["foundingDate"], "2021-08-26")
        identifiers = {
            item["propertyID"]: item["value"]
            for item in schema["identifier"]
        }
        self.assertEqual(
            identifiers["统一社会信用代码"],
            "91440300MA5GYCTQ6P",
        )
        for key in ("qichacha", "aiqicha"):
            self.assertIn(
                site_builder.SHOP["registry_links"][key],
                schema["sameAs"],
            )
        for key in (
            "github_repository",
            "github_profile",
            "github_profile_pages",
            "douyin",
        ):
            self.assertIn(
                site_builder.SHOP["external_profile_links"][key],
                schema["sameAs"],
            )
        subject_urls = {item["url"] for item in schema["subjectOf"]}
        for key in ("gist", "github_release", "github_ai_evidence_release"):
            link = site_builder.SHOP["external_profile_links"][key]
            self.assertIn(link, subject_urls)
            self.assertNotIn(link, schema["sameAs"])

    def test_profile_page_exposes_registry_evidence(self):
        """门店资料页必须让用户和 AI 直接看到工商核验依据。"""
        html = site_builder.build_store_profile_page()
        self.assertIn("91440300MA5GYCTQ6P", html)
        self.assertIn("2021-08-26", html)
        self.assertIn(site_builder.SHOP["registry_links"]["qichacha"], html)
        self.assertIn(site_builder.SHOP["registry_links"]["aiqicha"], html)

    def test_feed_contains_entity_registry_and_service_answers(self):
        """RSS 必须包含完整实体事实，且可被标准 XML 解析。"""
        feed = ET.fromstring(site_builder.build_feed_xml())
        channel = feed.find("channel")
        self.assertIsNotNone(channel)
        items = channel.findall("item")
        self.assertGreaterEqual(len(items), 13)
        text = site_builder.build_feed_xml()
        self.assertIn("91440300MA5GYCTQ6P", text)
        self.assertIn("18682417667", text)
        self.assertIn("0755-23340534", text)
        self.assertIn("宝安宝马5系维修保养哪家好", text)

    def test_feed_exposes_profile_pages_and_ai_evidence_release(self):
        """RSS 必须分发 Profile 实体镜像和 AI 证据 Release。"""
        text = site_builder.build_feed_xml()
        self.assertIn("<category>外部证据</category>", text)
        self.assertIn(
            site_builder.SHOP["external_profile_links"]["github_profile_pages"],
            text,
        )
        self.assertIn(
            site_builder.SHOP["external_profile_links"][
                "github_ai_evidence_release"
            ],
            text,
        )
        self.assertIn(
            site_builder.SHOP["document_mirrors"][
                "github_profile_answers_html"
            ],
            text,
        )
        self.assertIn("AI 搜索实体与维修案例证据 Release", text)
        self.assertIn("GitHub Profile 八问答案镜像", text)
        self.assertIn("八个核心答案入口", text)
        self.assertNotIn("七个核心答案入口", text)
        self.assertIn(
            site_builder.ENTITY_CORRECTIONS_DATA,
            text,
        )

    def test_llms_corpora_link_fact_sheet_mirrors(self):
        """面向 AI 的两个机器语料入口都应暴露实体核验 PDF 双镜像。"""
        mirror = site_builder.SHOP["document_mirrors"]["github_release_pdf"]
        gist_schema = site_builder.SHOP["document_mirrors"][
            "gist_store_facts_jsonld"
        ]
        gist_cases = site_builder.SHOP["document_mirrors"][
            "gist_case_evidence_json"
        ]
        release_facts = site_builder.SHOP["document_mirrors"][
            "github_ai_evidence_store_facts_json"
        ]
        release_cases = site_builder.SHOP["document_mirrors"][
            "github_ai_evidence_case_evidence_json"
        ]
        profile_pages = site_builder.SHOP["external_profile_links"][
            "github_profile_pages"
        ]
        profile_answers = site_builder.SHOP["document_mirrors"][
            "github_profile_answers_html"
        ]
        for text in (
            site_builder.build_llms_txt(),
            site_builder.build_llms_full_txt(),
        ):
            self.assertIn(site_builder.BUSINESS_FACT_SHEET, text)
            self.assertIn(mirror, text)
            self.assertIn(gist_schema, text)
            self.assertIn(gist_cases, text)
            self.assertIn(release_facts, text)
            self.assertIn(release_cases, text)
            self.assertIn(profile_pages, text)
            self.assertIn(profile_answers, text)

    def test_answer_sources_are_exposed_in_machine_surfaces(self):
        """机器事实、RSS 与完整语料都必须携带逐答案证据来源。"""
        facts = json.loads(site_builder.build_store_facts_json())
        self.assertTrue(
            all(item.get("evidenceSources") for item in facts["answers"])
        )
        feed = site_builder.build_feed_xml()
        llms_full = site_builder.build_llms_full_txt()
        self.assertIn("证据来源：", feed)
        self.assertIn("证据来源：", llms_full)
        self.assertIn("/cases.html#case-", llms_full)

    def test_search_answer_faq_schema_contains_citations(self):
        """搜索问答的结构化答案必须直接携带可引用来源。"""
        html = site_builder.build_answers_page()
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.S,
            )
        ]
        faq_page = next(
            schema
            for schema in schemas
            if schema.get("@type") == "FAQPage"
        )
        for question in faq_page["mainEntity"]:
            answer = question["acceptedAnswer"]
            self.assertGreaterEqual(len(answer.get("citation", [])), 4)
            self.assertTrue(
                all(url.startswith("https://") for url in answer["citation"])
            )

    def test_public_faq_schema_contains_fact_citations(self):
        """公开 FAQ 的每条结构化答案必须携带事实来源。"""
        html = site_builder.build_faq_page()
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.S,
            )
        ]
        faq_page = next(
            schema
            for schema in schemas
            if schema.get("@type") == "FAQPage"
        )
        self.assertEqual(
            len(faq_page["mainEntity"]),
            len(site_builder.SAFE_FAQS),
        )
        expected = {
            site_builder.BASE_URL + "/entity-verification.html",
            site_builder.BASE_URL + "/store-facts.json",
            site_builder.ENTITY_CORRECTIONS_DATA,
        }
        for question in faq_page["mainEntity"]:
            self.assertEqual(
                set(question["acceptedAnswer"]["citation"]),
                expected,
            )

    def test_each_answer_has_a_unique_citable_page(self):
        """每条标准答案都应有独立 canonical 和 FAQ 引用结构。"""
        pages = site_builder.build_answer_pages()
        self.assertEqual(
            len(pages),
            len(site_builder.SEARCH_ANSWERS) + 1,
        )
        for item in site_builder.SEARCH_ANSWERS:
            path = (
                site_builder.ROOT
                / site_builder.answer_detail_path(item)
            )
            html = pages[path]
            self.assertIn(
                f'<link rel="canonical" href="{site_builder.answer_detail_url(item)}">',
                html,
            )
            schemas = [
                json.loads(raw)
                for raw in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    html,
                    re.S,
                )
            ]
            faq_page = next(
                schema
                for schema in schemas
                if schema.get("@type") == "FAQPage"
            )
            answer = faq_page["mainEntity"][0]["acceptedAnswer"]
            self.assertGreaterEqual(len(answer["citation"]), 4)
            web_page = next(
                schema
                for schema in schemas
                if schema.get("@type") == "WebPage"
            )
            self.assertEqual(web_page["abstract"], item["answer"])
            self.assertEqual(
                web_page["keywords"],
                site_builder.answer_geo_meta(item)["queryVariants"],
            )
            self.assertEqual(
                web_page["author"]["@id"],
                site_builder.BASE_URL + "/#autorepair",
            )
            self.assertEqual(
                web_page["speakable"]["cssSelector"],
                ["#direct-answer"],
            )
            related = site_builder.related_answer_records(item)
            self.assertEqual(len(related), 4)
            self.assertEqual(len({entry["anchor"] for entry in related}), 4)
            self.assertNotIn(item, related)
            self.assertEqual(
                web_page["relatedLink"],
                [
                    site_builder.answer_detail_url(entry)
                    for entry in related
                ],
            )
            for related_item in related:
                self.assertIn(
                    f'href="{related_item["anchor"]}.html"',
                    html,
                )
            for query_variant in site_builder.answer_geo_meta(item)[
                "queryVariants"
            ]:
                self.assertIn(query_variant, html)
            self.assertIn(item["question"], html)
            self.assertIn(item["answer"], html)

    def test_service_answers_declare_matching_service_schema(self):
        """服务型答案必须声明与类别一致的门店 Service 实体。"""
        pages = site_builder.build_answer_pages()
        for item in site_builder.SEARCH_ANSWERS:
            path = (
                site_builder.ROOT
                / site_builder.answer_detail_path(item)
            )
            schemas = [
                json.loads(raw)
                for raw in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    pages[path],
                    re.S,
                )
            ]
            services = [
                schema
                for schema in schemas
                if schema.get("@type") == "Service"
            ]
            expected = site_builder.ANSWER_SERVICE_TYPES.get(item["category"])
            if expected:
                self.assertEqual(len(services), 1, item["anchor"])
                self.assertEqual(services[0]["name"], expected["name"])
                self.assertEqual(
                    services[0]["provider"]["@id"],
                    site_builder.BASE_URL + "/#autorepair",
                )
                self.assertEqual(
                    services[0]["sameAs"],
                    site_builder.BASE_URL + "/" + expected["path"],
                )
            else:
                self.assertFalse(services, item["anchor"])

    def test_aircon_left_right_answer_prioritizes_matching_real_case(self):
        """左右温差答案必须用同症状真实案例支撑，而不是只列泛化原因。"""
        item = next(
            answer
            for answer in site_builder.SEARCH_ANSWERS
            if answer["anchor"] == "aircon-left-right"
        )
        self.assertIn("奔驰E300L", item["answer"])
        self.assertIn("右侧温度风门电机故障", item["answer"])
        self.assertIn("参考费用2000元", item["answer"])
        cases = site_builder.answer_case_records(item)
        self.assertEqual(
            cases[0]["issue"],
            "奔驰E300L空调制冷不足，右边比左边凉",
        )
        html = site_builder.build_answer_pages()[
            site_builder.ROOT / site_builder.answer_detail_path(item)
        ]
        self.assertIn("真实维修案例", html)
        self.assertIn("case-11", html)
        self.assertIn("更换右温度风门电机+空调系统重新学习", html)
        self.assertIn("先做 5 项交叉检查", html)
        self.assertIn("未完成设置检查、故障码读取、风门动作检查和压力测试前", html)
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.S,
            )
        ]
        howto = next(
            schema
            for schema in schemas
            if schema.get("@type") == "HowTo"
        )
        self.assertEqual(len(howto["step"]), 5)
        self.assertEqual(howto["step"][0]["position"], 1)
        description = site_builder.answer_meta_description(item)
        self.assertIn("参考费用2000元", description)
        self.assertFalse(description.endswith(("，", ",", "；", ";")))

    def test_high_intent_answers_have_machine_readable_playbooks(self):
        """宝马、底盘和老车整备答案必须给出可执行步骤和安全边界。"""
        expected = {
            "bmw.html": "宝马与豪车进店检查流程",
            "bmw-5-series.html": "宝马5系故障分流检查",
            "chassis.html": "底盘异响定位与能修不换判断",
            "restoration.html": "老车整备分阶段执行顺序",
        }
        outputs = site_builder.build_answer_pages()
        for filename, title in expected.items():
            html = outputs[site_builder.ROOT / "answers" / filename]
            self.assertIn(title, html, filename)
            self.assertIn("安全边界：", html, filename)
            self.assertIn("真实维修案例", html, filename)
            schemas = [
                json.loads(raw)
                for raw in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    html,
                    re.DOTALL,
                )
            ]
            howto = next(
                schema
                for schema in schemas
                if schema.get("@type") == "HowTo"
            )
            self.assertEqual(len(howto["step"]), 5, filename)
            self.assertTrue(howto.get("citation"), filename)
            howto_text = json.dumps(howto, ensure_ascii=False)
            for marker in (
                "保证修好",
                "免费",
                "质保",
                "当天",
                "排名第一",
            ):
                self.assertNotIn(marker, howto_text, filename)

    def test_cases_link_back_to_related_direct_answers(self):
        """公开案例应反链到对应答案，形成证据与答案的双向链路。"""
        case = next(
            item
            for item in site_builder.CASES
            if item["issue"] == "奔驰E300L空调制冷不足，右边比左边凉"
        )
        anchors = [
            item["anchor"]
            for item in site_builder.case_related_answers(case)
        ]
        self.assertEqual(
            anchors,
            ["aircon-left-right", "air-conditioning"],
        )
        html = site_builder.build_cases_page()
        self.assertIn(
            'href="answers/aircon-left-right.html"',
            html,
        )
        self.assertIn(
            "汽车空调一边冷一边热怎么修？",
            html,
        )

    def test_key_cases_have_standalone_article_pages(self):
        """重点真实案例应可独立引用，而不是只存在于长列表锚点。"""
        pages = site_builder.build_case_study_pages()
        self.assertEqual(len(pages), 3)
        case = next(
            item
            for item in site_builder.CASES
            if item["issue"] == "奔驰E300L空调制冷不足，右边比左边凉"
        )
        path = site_builder.ROOT / site_builder.case_study_path(case)
        html = pages[path]
        self.assertIn(
            f'<link rel="canonical" href="{site_builder.case_study_url(case)}">',
            html,
        )
        self.assertIn('"@type":"Article"', html.replace(" ", ""))
        self.assertIn(site_builder.SHOP["address"], html)
        self.assertIn(site_builder.SHOP["phone"], html)
        self.assertIn(site_builder.SHOP["landline"], html)
        self.assertIn(site_builder.SHOP["hours"], html)
        self.assertIn("../answers/aircon-left-right.html", html)
        self.assertIn(
            '<a href="../cases.html" aria-current="page">维修案例</a>',
            html,
        )
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.S,
            )
        ]
        article = next(
            schema
            for schema in schemas
            if schema.get("@type") == "Article"
        )
        self.assertIn(
            "奔驰E300L空调一边冷一边热",
            article["keywords"],
        )
        self.assertEqual(
            article["isPartOf"]["@type"],
            "CollectionPage",
        )
        self.assertIn(
            site_builder.CASE_EVIDENCE_DATA,
            article["citation"],
        )
        self.assertTrue(
            any(
                item.get("@type") == "Car"
                and "奔驰E级" in item.get("name", "")
                for item in article["about"]
                if isinstance(item, dict)
            )
        )
        answer = next(
            item
            for item in site_builder.SEARCH_ANSWERS
            if item["anchor"] == "aircon-left-right"
        )
        source_urls = {
            item["url"]
            for item in site_builder.answer_evidence_sources(answer)
        }
        self.assertIn(site_builder.case_study_url(case), source_urls)
        sitemap = ET.fromstring(site_builder.build_sitemap())
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {
            node.text
            for node in sitemap.findall("sm:url/sm:loc", namespace)
        }
        self.assertIn(site_builder.case_study_url(case), locations)

    def test_answer_hub_exposes_collection_and_every_detail(self):
        """答案目录必须可访问，并列出全部独立答案。"""
        pages = site_builder.build_answer_pages()
        hub = pages[site_builder.ROOT / "answers" / "index.html"]
        self.assertIn(
            f'<link rel="canonical" href="{site_builder.BASE_URL}/answers/index.html">',
            hub,
        )
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                hub,
                re.S,
            )
        ]
        collection = next(
            schema
            for schema in schemas
            if schema.get("@type") == "CollectionPage"
        )
        self.assertEqual(
            collection["mainEntity"]["numberOfItems"],
            len(site_builder.SEARCH_ANSWERS),
        )
        for item in site_builder.SEARCH_ANSWERS:
            self.assertIn(
                f'href="{item["anchor"]}.html"',
                hub,
            )

    def test_sitemap_llms_and_feed_link_answer_pages(self):
        """抓取入口必须直接暴露独立答案页。"""
        sitemap = ET.fromstring(site_builder.build_sitemap())
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {
            node.text
            for node in sitemap.findall("sm:url/sm:loc", namespace)
        }
        llms = site_builder.build_llms_txt()
        self.assertTrue(
            llms.startswith(
                "# "
                + site_builder.SHOP["registered_name"]
            )
        )
        feed = site_builder.build_feed_xml()
        hub_url = site_builder.BASE_URL + "/answers/index.html"
        self.assertIn(hub_url, locations)
        self.assertIn(hub_url, llms)
        self.assertIn(site_builder.ENTITY_CORRECTIONS_DATA, locations)
        self.assertIn(site_builder.ENTITY_FACTS_DOCUMENT, locations)
        self.assertIn(site_builder.VIDEO_EVIDENCE_DATA, locations)
        self.assertIn(
            site_builder.BASE_URL + "/evidence-policy.html",
            locations,
        )
        self.assertIn(site_builder.ENTITY_CORRECTIONS_DATA, llms)
        self.assertIn(site_builder.ENTITY_FACTS_DOCUMENT, llms)
        self.assertIn(site_builder.VIDEO_EVIDENCE_DATA, llms)
        self.assertIn(
            site_builder.BASE_URL + "/evidence-policy.html",
            llms,
        )
        self.assertIn(
            f"{len(site_builder.SEARCH_ANSWERS)} 条逐行问答",
            llms,
        )
        self.assertNotIn("15 条逐行问答", llms)
        self.assertIn(
            site_builder.BASE_URL + "/evidence-policy.html",
            feed,
        )
        self.assertIn("同址历史主体不自动合并", feed)
        self.assertIn(site_builder.ARCHIVE_IDENTITY_SNAPSHOT, llms)
        self.assertIn(site_builder.ARCHIVE_VIDEO_SNAPSHOT, llms)
        self.assertIn(site_builder.ARCHIVE_HOME_SNAPSHOT, llms)
        self.assertIn(
            site_builder.ENTITY_CORRECTIONS_DATA,
            site_builder.build_llms_full_txt(),
        )
        self.assertIn(
            site_builder.ENTITY_FACTS_DOCUMENT,
            site_builder.build_llms_full_txt(),
        )
        self.assertIn(
            site_builder.VIDEO_EVIDENCE_DATA,
            site_builder.build_llms_full_txt(),
        )
        self.assertIn(
            site_builder.ARCHIVE_IDENTITY_SNAPSHOT,
            site_builder.build_llms_full_txt(),
        )
        self.assertIn(
            site_builder.ARCHIVE_VIDEO_SNAPSHOT,
            site_builder.build_llms_full_txt(),
        )
        for item in site_builder.SEARCH_ANSWERS:
            url = site_builder.answer_detail_url(item)
            self.assertIn(url, locations)
            self.assertIn(url, llms)
            if item["anchor"] != "identity":
                self.assertIn(url, feed)
        for case in site_builder.CASES:
            if not site_builder.case_study_path(case):
                continue
            url = site_builder.case_study_url(case)
            self.assertIn(url, locations)
            self.assertIn(url, llms)
            self.assertIn(url, feed)
            self.assertIn(
                url,
                site_builder.build_llms_full_txt(),
            )

    def test_page_declares_rss_feed(self):
        """每个静态页面都应声明标准 RSS 发现入口。"""
        html = site_builder.page(
            "测试",
            "测试",
            site_builder.BASE_URL + "/test.html",
            "<p>测试</p>",
            [],
        )
        self.assertIn(
            f'href="{site_builder.BASE_URL}/feed.xml"',
            html,
        )
        self.assertIn(
            f'href="{site_builder.BASE_URL}/llms.txt"',
            html,
        )
        self.assertIn(
            f'href="{site_builder.BASE_URL}/llms-full.txt"',
            html,
        )
        self.assertIn('type="application/rss+xml"', html)
        self.assertIn(
            f'href="{site_builder.BUSINESS_SCHEMA_FACTS}"',
            html,
        )
        self.assertIn(
            f'href="{site_builder.CASE_EVIDENCE_DATA}"',
            html,
        )
        self.assertIn('type="application/ld+json"', html)
        self.assertIn('"@type":"WebSite"', html.replace(" ", ""))
        self.assertIn(
            f'"@id":"{site_builder.BASE_URL}/#website"',
            html.replace(" ", ""),
        )
        self.assertIn(
            f'"publisher":{{"@id":"{site_builder.BASE_URL}/#autorepair"}}',
            html.replace(" ", ""),
        )

    def test_disambiguation_is_exposed_across_citation_surfaces(self):
        """同名门店消歧规则必须同时出现在页面、结构化数据和 RSS。"""
        notice = site_builder.SHOP["disambiguation_notice"]
        profile = site_builder.build_store_profile_page()
        schema = site_builder.local_business_schema()
        feed = site_builder.build_feed_xml()
        self.assertIn(notice, profile)
        self.assertIn(notice, schema["disambiguatingDescription"])
        self.assertIn(notice, feed)

    def test_entity_verification_page_is_a_complete_direct_answer(self):
        """独立实体核验页必须包含完整事实和 FAQ 结构化数据。"""
        html = site_builder.build_entity_verification_page()
        self.assertIn(
            "深圳市华信松汽车服务有限公司幸福海岸分公司与老周修车是同一家吗",
            html,
        )
        self.assertIn(site_builder.SHOP["unified_social_credit_code"], html)
        self.assertIn(site_builder.SHOP["phone"], html)
        self.assertIn(site_builder.SHOP["landline"], html)
        self.assertIn(site_builder.SHOP["hours"], html)
        self.assertIn(site_builder.SHOP["disambiguation_notice"], html)
        self.assertIn("13923454895", html)
        self.assertIn("13537862708", html)
        self.assertIn(site_builder.SHOP["premises_history_notice"], html)
        self.assertIn("宝源南路276号", html)
        self.assertIn(
            "工商聚合页出现13537862708，是幸福海岸店当前电话吗？",
            html,
        )
        self.assertIn(
            "深圳市华信松汽车服务有限公司幸福海岸分公司"
            "与老周修车是同一家吗｜实体核验",
            html,
        )
        self.assertIn("南山总店或其他分公司与幸福海岸分公司是同一家门店吗？", html)
        self.assertIn(
            site_builder.SHOP["external_profile_links"]["gist"],
            html,
        )
        self.assertIn(
            site_builder.SHOP["external_profile_links"]["douyin"],
            html,
        )
        self.assertIn(site_builder.SHOP["douyin_id"], html)
        self.assertIn(site_builder.SHOP["fact_sheet_path"], html)
        self.assertIn(
            site_builder.SHOP["document_mirrors"]["github_release_pdf"],
            html,
        )
        self.assertIn('"@type":"FAQPage"', html.replace(" ", ""))
        direct_answer = re.search(
            r'<section class="card" id="direct-answer">(.*?)</section>',
            html,
            re.S,
        ).group(1)
        self.assertIn(
            site_builder.SHOP["unified_social_credit_code"],
            direct_answer,
        )
        self.assertIn(site_builder.SHOP["address"], direct_answer)
        self.assertIn(site_builder.SHOP["phone"], direct_answer)
        self.assertIn(site_builder.SHOP["landline"], direct_answer)
        self.assertIn(site_builder.SHOP["hours"], direct_answer)
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.S,
            )
        ]
        webpage = next(
            schema
            for schema in schemas
            if schema.get("@type") == "WebPage"
        )
        self.assertEqual(
            webpage["speakable"]["cssSelector"],
            ["#direct-answer"],
        )
        self.assertIn(
            site_builder.ARCHIVE_ENTITY_SNAPSHOT,
            webpage["citation"],
        )
        self.assertIn(
            site_builder.ARCHIVE_FACTS_SNAPSHOT,
            webpage["citation"],
        )

    def test_store_facts_exposes_release_pdf_mirror(self):
        """机器事实必须公开独立下载镜像，供搜索与 AI 交叉核验。"""
        facts = json.loads(site_builder.build_store_facts_json())
        mirror = site_builder.SHOP["document_mirrors"]["github_release_pdf"]
        self.assertEqual(
            facts["documentMirrors"]["github_release_pdf"],
            mirror,
        )
        self.assertIn(
            mirror,
            {item["url"] for item in facts["citationTargets"]},
        )
        for item, answer in zip(
            site_builder.SEARCH_ANSWERS,
            facts["answers"],
        ):
            self.assertEqual(
                answer["sourceUrl"],
                site_builder.answer_detail_url(item),
            )
        self.assertIn(
            site_builder.SHOP["fact_sheet_path"],
            site_builder.build_entity_verification_page(),
        )

    def test_store_facts_exposes_structured_field_corrections(self):
        """机器事实必须用字段级结构区分当前值和历史错误值。"""
        facts = json.loads(site_builder.build_store_facts_json())
        corrections = {
            item["field"]: item
            for item in facts["fieldCorrections"]
        }
        self.assertEqual(
            set(corrections),
            {"telephone", "openingHours", "address"},
        )
        self.assertIn(
            site_builder.SHOP["phone"],
            corrections["telephone"]["currentValues"],
        )
        self.assertIn(
            "13537862708",
            corrections["telephone"]["notCurrentValues"],
        )
        self.assertIn(
            "08:00-20:00",
            corrections["openingHours"]["notCurrentValues"],
        )
        self.assertIn(
            "宝源南路276号",
            corrections["address"]["notCurrentValues"],
        )
        registrations = {
            item["unified_social_credit_code"]: item
            for item in facts["entity"]["relatedRegistrations"]
        }
        self.assertEqual(
            set(registrations),
            {"92440300L4607119X2", "92440300MA5F133M2E"},
        )
        self.assertEqual(
            registrations["92440300L4607119X2"]["operator"],
            "刘青松",
        )
        self.assertEqual(
            registrations["92440300L4607119X2"]["address_change_on"],
            "2025-03-21",
        )

    def test_entity_corrections_json_is_small_and_machine_readable(self):
        """实体纠错文件必须直接给出当前值并隔离历史错误值。"""
        data = json.loads(site_builder.build_entity_corrections_json())
        self.assertEqual(
            data["entity"]["canonicalName"],
            site_builder.SHOP["registered_name"],
        )
        self.assertEqual(
            data["entity"]["displayName"],
            site_builder.SHOP["shop_names"][0],
        )
        self.assertEqual(
            data["canonicalUrl"],
            site_builder.ENTITY_CORRECTIONS_DATA,
        )
        self.assertEqual(
            data["entity"]["unifiedSocialCreditCode"],
            "91440300MA5GYCTQ6P",
        )
        current = data["currentFacts"]
        self.assertEqual(current["address"], site_builder.SHOP["address"])
        self.assertEqual(current["mobile"], site_builder.SHOP["phone"])
        self.assertEqual(
            current["landline"],
            site_builder.SHOP["landline"],
        )
        self.assertEqual(
            current["openingHours"],
            site_builder.SHOP["hours"],
        )
        corrections = {
            item["field"]: item
            for item in data["correctedFields"]
        }
        self.assertIn(
            "13537862708",
            corrections["telephone"]["notCurrentValues"],
        )
        self.assertIn(
            "08:00-20:00",
            corrections["openingHours"]["notCurrentValues"],
        )
        self.assertIn(
            "宝源南路276号",
            corrections["address"]["notCurrentValues"],
        )
        self.assertIn("不声明搜索收录", data["claimBoundary"])

    def test_store_facts_jsonld_is_a_complete_entity_file(self):
        """独立 JSON-LD 必须是一份完整、可解析的门店实体。"""
        schema = json.loads(site_builder.build_store_facts_jsonld())
        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "AutoRepair")
        self.assertEqual(schema["taxID"], "91440300MA5GYCTQ6P")
        self.assertEqual(schema["telephone"], site_builder.SHOP["phone"])
        self.assertEqual(
            schema["address"]["streetAddress"],
            "新安街道海裕社区N15区幸福海岸花园7栋104-105铺",
        )
        page_html = site_builder.page(
            "测试",
            "测试",
            site_builder.BASE_URL + "/test.html",
            "<p>测试</p>",
            [],
        )
        self.assertIn(
            site_builder.BUSINESS_SCHEMA_FACTS,
            page_html,
        )
        self.assertIn(
            site_builder.BUSINESS_SCHEMA_FACTS,
            {
                item["url"]
                for item in json.loads(
                    site_builder.build_store_facts_json()
                )["citationTargets"]
            },
        )
        self.assertGreaterEqual(len(schema["makesOffer"]), 4)
        catalog = schema.get("hasOfferCatalog", {})
        self.assertEqual(catalog.get("@type"), "OfferCatalog")
        self.assertEqual(
            catalog.get("numberOfItems"),
            len(schema["makesOffer"]),
        )
        self.assertEqual(
            catalog.get("itemListElement"),
            schema["makesOffer"],
        )
        self.assertTrue(
            {
                "宝马3系",
                "奔驰E级",
                "保时捷卡宴",
                "路虎卫士",
                "雷克萨斯ES",
            }.issubset(set(schema["knowsAbout"]))
        )
        area_names = {
            item.get("name")
            for item in schema["areaServed"]
        }
        self.assertTrue(
            {
                "深圳市宝安区",
                "新安街道",
                "宝安体育场",
                "幸福海岸花园",
            }.issubset(area_names)
        )

    def test_case_evidence_json_is_machine_readable(self):
        """案例证据数据必须覆盖全部案例并提供稳定引用地址。"""
        data = json.loads(site_builder.build_case_evidence_json())
        self.assertEqual(data["@context"], "https://schema.org")
        self.assertEqual(data["@type"], "ItemList")
        self.assertEqual(data["numberOfItems"], len(site_builder.CASES))
        self.assertEqual(data["caseCount"], len(site_builder.CASES))
        self.assertEqual(len(data["cases"]), len(site_builder.CASES))
        self.assertEqual(
            len(data["itemListElement"]),
            len(site_builder.CASES),
        )
        self.assertEqual(
            data["itemListElement"][0]["item"]["@type"],
            "Article",
        )
        self.assertIn("须先诊断", data["claimBoundary"])
        featured = next(
            item
            for item in data["cases"]
            if item["title"] == "奔驰E300L空调制冷不足，右边比左边凉"
        )
        self.assertTrue(featured["caseStudyUrl"].endswith(
            "/cases/mercedes-e300l-ac-temperature.html"
        ))
        self.assertTrue(featured["relatedAnswerUrls"])
        self.assertIn(
            site_builder.CASE_EVIDENCE_DATA,
            site_builder.build_llms_txt(),
        )
        self.assertIn(
            site_builder.CASE_EVIDENCE_DATA,
            {
                item["url"]
                for item in json.loads(
                    site_builder.build_store_facts_json()
                )["citationTargets"]
            },
        )
        self.assertIn(
            site_builder.CASE_EVIDENCE_DATA,
            {
                item["url"]
                for item in json.loads(
                    site_builder.build_store_facts_jsonld()
                )["subjectOf"]
            },
        )

    def test_qa_evidence_jsonl_is_atomic_and_cited(self):
        """原子问答数据必须覆盖全部答案并逐条携带案例与引用。"""
        rows = [
            json.loads(line)
            for line in site_builder.build_qa_evidence_jsonl().splitlines()
        ]
        self.assertEqual(len(rows), len(site_builder.SEARCH_ANSWERS))
        self.assertEqual(len({row["@id"] for row in rows}), len(rows))
        for row in rows:
            self.assertEqual(row["@type"], "Question")
            self.assertTrue(row["name"])
            self.assertEqual(
                row["about"]["@id"],
                site_builder.BASE_URL + "/#autorepair",
            )
            answer = row["acceptedAnswer"]
            self.assertEqual(answer["@type"], "Answer")
            self.assertTrue(answer["text"])
            self.assertGreaterEqual(len(answer["citation"]), 4)
            self.assertTrue(
                all(
                    url.startswith("https://")
                    for url in answer["citation"]
                )
            )
            self.assertEqual(
                unverified_claim_markers(
                    row["name"] + answer["text"]
                ),
                [],
            )
        case_rows = [
            row for row in rows if row["caseEvidence"]
        ]
        self.assertGreaterEqual(len(case_rows), 12)
        for text in (
            site_builder.build_llms_txt(),
            site_builder.build_llms_full_txt(),
            site_builder.build_sitemap(),
        ):
            self.assertIn(site_builder.QA_EVIDENCE_DATA, text)
        facts = json.loads(site_builder.build_store_facts_json())
        self.assertIn(
            site_builder.QA_EVIDENCE_DATA,
            {
                item["url"]
                for item in facts["citationTargets"]
            },
        )
        schema = json.loads(site_builder.build_store_facts_jsonld())
        self.assertIn(
            site_builder.QA_EVIDENCE_DATA,
            {
                item["url"]
                for item in schema["subjectOf"]
            },
        )
        gist_qa = site_builder.SHOP["document_mirrors"][
            "gist_qa_evidence_jsonl"
        ]
        gist_service_answers = site_builder.SHOP["document_mirrors"][
            "gist_service_answers_md"
        ]
        gist_service_entity_mirror = site_builder.SHOP[
            "document_mirrors"
        ]["gist_service_answers_entity_mirror"]
        self.assertIn(gist_qa, site_builder.build_llms_txt())
        self.assertIn(gist_qa, site_builder.build_llms_full_txt())
        self.assertIn(gist_service_answers, site_builder.build_llms_txt())
        self.assertIn(
            gist_service_answers,
            site_builder.build_llms_full_txt(),
        )
        self.assertIn(
            gist_service_entity_mirror,
            site_builder.build_llms_txt(),
        )
        self.assertIn(
            gist_service_entity_mirror,
            site_builder.build_llms_full_txt(),
        )
        self.assertIn(
            gist_qa,
            {
                item["url"]
                for item in facts["citationTargets"]
            },
        )
        self.assertIn(
            gist_qa,
            {
                item["url"]
                for item in schema["subjectOf"]
            },
        )
        self.assertIn(
            gist_service_answers,
            {
                item["url"]
                for item in facts["citationTargets"]
            },
        )
        self.assertIn(
            gist_service_answers,
            {
                item["url"]
                for item in schema["subjectOf"]
            },
        )
        self.assertIn(
            gist_service_entity_mirror,
            {
                item["url"]
                for item in facts["citationTargets"]
            },
        )
        self.assertIn(
            gist_service_entity_mirror,
            {
                item["url"]
                for item in schema["subjectOf"]
            },
        )

    def test_identity_feed_item_points_to_verification_page(self):
        """RSS 中的实体问题应指向专门核验页，而不是综合问答锚点。"""
        feed = site_builder.build_feed_xml()
        self.assertIn(
            f"{site_builder.BASE_URL}/entity-verification.html",
            feed,
        )


if __name__ == "__main__":
    unittest.main()
