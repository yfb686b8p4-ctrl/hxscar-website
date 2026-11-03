#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证站外发布内容不会生成虚构评价或未经核验的承诺。"""

import json
import random
import re
import unittest

import multi_platform_publisher as publisher
import weekly_rotation
from content_safety_rules import (
    unverified_claim_markers,
    unverified_faq_markers,
    partition_faqs,
)
from data_loader import ADDRESS, PHONE
from scripts import authority_queue, site_builder


class ContentSafetyTests(unittest.TestCase):
    """把未核验营销话术挡在发布队列之前。"""

    def test_platform_drafts_use_real_facts_without_unverified_claims(self):
        random.seed(44 * 7919)
        generators = (
            publisher.generate_dianping,
            publisher.generate_xiaohongshu,
            publisher.generate_douyin,
            publisher.generate_58,
            publisher.generate_meituan,
            publisher.generate_map,
        )
        banned = (
            "4.9+",
            "服务超1000台",
            "⭐⭐⭐⭐⭐",
            "评分：",
            "推荐评价文案",
            "团队10年以上",
            "免费检测",
            "质保无忧",
            "当天可取",
            "省一半",
            "原价：¥",
            "团购价：",
        )
        for generator in generators:
            content = generator(44)
            self.assertIn(ADDRESS, content, generator.__name__)
            self.assertIn(PHONE, content, generator.__name__)
            for marker in banned:
                self.assertNotIn(marker, content, generator.__name__)

    def test_publish_queue_blocks_unverified_claims(self):
        matches = authority_queue.unverified_claim_matches(
            "推荐评价文案：评分：⭐⭐⭐⭐⭐，4.9+，服务超1000台。"
        )
        self.assertEqual(
            set(matches),
            {"推荐评价文案", "评分：", "⭐⭐⭐⭐⭐", "4.9+", "服务超1000台"},
        )
        self.assertEqual(authority_queue.unverified_claim_matches("真实案例"), [])

    def test_committed_publish_queues_have_content_sources(self):
        """已生成队列不得留下找不到内容源的空白任务。"""
        queue_root = site_builder.ROOT / "publishing" / "queue"
        manifests = sorted(queue_root.glob("W*/manifest.json"))
        self.assertTrue(manifests)
        for manifest_path in manifests:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
            for task in manifest["tasks"]:
                self.assertTrue(
                    task["source_file"],
                    f"{manifest_path.parent.name}:{task['id']}",
                )
                self.assertTrue(
                    (site_builder.ROOT / task["source_file"]).is_file(),
                    f"{manifest_path.parent.name}:{task['id']}",
                )
                task_text = (
                    site_builder.ROOT / task["task_file"]
                ).read_text(encoding="utf-8")
                self.assertNotIn(
                    "未找到本周内容源",
                    task_text,
                    f"{manifest_path.parent.name}:{task['id']}",
                )

    def test_gist_service_answers_are_complete_and_safe(self):
        """外部 Gist 服务答案必须保留实体事实并排除未核实承诺。"""
        text = (
            site_builder.ROOT
            / "publishing"
            / "gist"
            / "SERVICE_ANSWERS.md"
        ).read_text(encoding="utf-8")
        for marker in (
            ADDRESS,
            PHONE,
            "0755-23340534",
            "宝马专修",
            "汽车空调不凉",
            "底盘异响",
            "老车整备",
            "不声明已经获得搜索收录、AI 引用或排名",
        ):
            self.assertIn(marker, text)
        self.assertEqual(unverified_claim_markers(text), [])

    def test_sogou_lizhi_queue_uses_prepared_application(self):
        """立知任务必须直接使用项目内申请包，而不是虚构周更文件。"""
        config = json.loads(
            (
                site_builder.ROOT
                / "config"
                / "external_platforms.json"
            ).read_text(encoding="utf-8")
        )
        platform = next(
            item
            for item in config["platforms"]
            if item["id"] == "sogou-lizhi"
        )
        source = authority_queue.resolve_content_source(platform, 44)
        self.assertTrue(source.is_file())
        self.assertEqual(source.name, "application.md")
        self.assertIn("尚未发送", source.read_text(encoding="utf-8"))

    def test_homepage_uses_public_evidence_instead_of_review_excerpts(self):
        config, _ = weekly_rotation.select_config(44)
        html = weekly_rotation.build_page(
            config,
            random.sample(weekly_rotation.ALL_CASES, 6),
            44,
        )
        self.assertNotIn("车主评价摘录", html)
        self.assertNotIn("团队拥有10年以上", html)
        self.assertNotIn("4.9+", html)
        self.assertNotIn("服务超1000台", html)
        self.assertIn("公开核验与机器资料", html)
        self.assertIn("entity-verification.html", html)
        self.assertIn("case-evidence.json", html)
        self.assertIn('"@type":"OfferCatalog"', html.replace(" ", ""))
        self.assertIn("雷克萨斯ES", html)
        self.assertNotIn("parentOrganization", html)

    def test_machine_faq_schema_excludes_unverified_claims(self):
        safe, blocked = partition_faqs(weekly_rotation.ALL_FAQS)
        self.assertTrue(safe)
        self.assertTrue(blocked)
        self.assertTrue(
            all(
                not unverified_faq_markers(item)
                for item in safe
            )
        )
        self.assertTrue(all(entry["markers"] for entry in blocked))

        html = site_builder.build_faq_page()
        faq_schemas = []
        for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.DOTALL,
        ):
            schema = json.loads(raw)
            if schema.get("@type") == "FAQPage":
                faq_schemas.append(schema)
        self.assertEqual(len(faq_schemas), 1)
        self.assertEqual(
            faq_schemas[0]["about"]["@id"],
            site_builder.BASE_URL + "/#autorepair",
        )
        self.assertTrue(faq_schemas[0].get("dateModified"))
        for question in faq_schemas[0]["mainEntity"]:
            claim = (
                question["name"]
                + question["acceptedAnswer"]["text"]
            )
            self.assertEqual(unverified_claim_markers(claim), [])

    def test_public_faq_page_only_shows_safe_subset(self):
        """公开 FAQ 页面正文不得重新出现被隔离问题。"""
        html = site_builder.build_faq_page()
        self.assertEqual(html.count('class="faq-item"'), len(site_builder.SAFE_FAQS))
        _, blocked = partition_faqs(site_builder.FAQS)
        for entry in blocked:
            self.assertNotIn(entry["item"]["question"], html)

    def test_all_generated_machine_faq_schemas_use_safe_subset(self):
        """所有页面型 FAQ 结构化数据均不得重新引入旧营销承诺。"""
        pages = [
            site_builder.ROOT / "index.html",
            site_builder.ROOT / "faq.html",
            *sorted((site_builder.ROOT / "services").glob("*.html")),
            *sorted((site_builder.ROOT / "models").glob("*.html")),
        ]
        for path in pages:
            html = path.read_text(encoding="utf-8")
            for raw in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html,
                re.DOTALL,
            ):
                schema = json.loads(raw)
                if schema.get("@type") != "FAQPage":
                    continue
                for question in schema.get("mainEntity", []):
                    item = {
                        "question": question.get("name", ""),
                        "answer": question.get("acceptedAnswer", {}).get(
                            "text", ""
                        ),
                    }
                    matches = unverified_faq_markers(item)
                    self.assertEqual(
                        matches,
                        [],
                        f"{path.relative_to(site_builder.ROOT)}: "
                        f"{item['question']}",
                    )

    def test_llms_full_does_not_leak_blocked_faqs(self):
        """完整机器语料只能出现安全子集中的问题。"""
        llms_full = site_builder.build_llms_full_txt()
        _, blocked = partition_faqs(weekly_rotation.ALL_FAQS)
        for entry in blocked:
            self.assertNotIn(
                f"### {entry['item'][0]}",
                llms_full,
            )


if __name__ == "__main__":
    unittest.main()
