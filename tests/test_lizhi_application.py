#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证立知 TOP1 问答申请包可核验且不含未证实承诺。"""

import json
import unittest
import zipfile
from pathlib import Path

from content_safety_rules import unverified_faq_markers
from scripts import build_lizhi_application


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = (
    ROOT / "publishing" / "lizhi" / "2026-11-01"
)


class LizhiApplicationTests(unittest.TestCase):
    """确保邮件申请包与实际证据边界一致。"""

    def test_application_package_counts_and_safety(self):
        facts = build_lizhi_application.load_json(
            ROOT / "store-facts.json"
        )
        faqs = build_lizhi_application.load_json(
            ROOT / "data" / "faqs.json"
        )
        cases = build_lizhi_application.load_json(
            ROOT / "case-evidence.json"
        )
        files, manifest = build_lizhi_application.build_payloads(
            facts,
            faqs,
            cases,
        )
        counts = manifest["counts"]
        self.assertEqual(
            counts["answers"],
            len(facts["answers"]),
        )
        self.assertEqual(counts["safeFaqs"], 77)
        self.assertEqual(
            counts["totalQa"],
            len(facts["answers"]) + counts["safeFaqs"],
        )
        self.assertEqual(counts["cases"], 56)
        self.assertEqual(counts["blockedFaqs"], 65)
        self.assertEqual(manifest["status"], "prepared_not_sent")
        self.assertIn("尚未发送", files["application.md"])
        self.assertIn("zzpt@tencent.com", files["application.md"])
        self.assertIn("91440300MA5GYCTQ6P", files["application.md"])
        self.assertIn("不表示已经获得立知合作", files["application.md"])

        for line in files["sample-answers.jsonl"].splitlines():
            item = json.loads(line)
            self.assertTrue(item["question"])
            self.assertTrue(item["answer"])
            self.assertTrue(item["sourceUrl"].startswith("https://"))
            self.assertGreaterEqual(len(item["citations"]), 4)
            self.assertEqual(
                unverified_faq_markers(
                    {
                        "question": item["question"],
                        "answer": item["answer"],
                    }
                ),
                [],
            )

        for line in files["sample-safe-faq.jsonl"].splitlines():
            item = json.loads(line)
            self.assertEqual(
                unverified_faq_markers(
                    {
                        "question": item["question"],
                        "answer": item["answer"],
                    }
                ),
                [],
            )

    def test_application_archive_contains_required_files(self):
        archive_path = (
            OUTPUT_DIR / "sogou-lizhi-application-2026-11-01.zip"
        )
        self.assertTrue(archive_path.is_file())
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
        self.assertTrue(
            {
                "application.md",
                "sample-answers.jsonl",
                "sample-answers.csv",
                "sample-safe-faq.jsonl",
                "sample-cases.jsonl",
                "manifest.json",
            }.issubset(names)
        )


if __name__ == "__main__":
    unittest.main()
