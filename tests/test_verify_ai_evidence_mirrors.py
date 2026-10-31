#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 AI 证据镜像一致性检查器。"""

import unittest
from pathlib import Path

from scripts import verify_ai_evidence_mirrors


ROOT = Path(__file__).resolve().parent.parent


class VerifyAiEvidenceMirrorsTests(unittest.TestCase):
    """保证一致性门禁能识别镜像结构问题。"""

    def test_local_qa_evidence_passes_structure_checks(self):
        payload = (ROOT / "qa-evidence.jsonl").read_bytes()
        result = verify_ai_evidence_mirrors.evaluate_qa_payload(payload)
        self.assertEqual(
            result["rows"],
            verify_ai_evidence_mirrors.EXPECTED_QA_ROWS,
        )
        self.assertEqual(
            result["unique_ids"],
            verify_ai_evidence_mirrors.EXPECTED_QA_ROWS,
        )
        self.assertGreaterEqual(result["with_cases"], 12)
        self.assertGreaterEqual(result["min_citations"], 15)
        self.assertEqual(result["errors"], [])

    def test_verifier_requires_four_mirrors(self):
        names = {
            item["name"]
            for item in verify_ai_evidence_mirrors.MIRRORS
        }
        self.assertEqual(
            names,
            {
                "本地构建",
                "官网",
                "Profile Pages",
                "GitHub Release",
                "GitHub Gist",
                "jsDelivr",
            },
        )
        fact_names = {
            item["name"]
            for item in verify_ai_evidence_mirrors.FACT_MIRRORS
        }
        self.assertEqual(
            fact_names,
            {
                "本地门店事实",
                "本地门店JSON-LD",
                "官网门店事实",
                "Release门店事实",
                "官网门店JSON-LD",
                "Release门店JSON-LD",
                "Gist门店JSON-LD",
                "jsDelivr门店事实",
                "jsDelivr门店JSON-LD",
            },
        )
        correction_names = {
            item["name"]
            for item in verify_ai_evidence_mirrors.CORRECTION_MIRRORS
        }
        self.assertEqual(
            correction_names,
            {
                "本地门店纠错JSON",
                "官网门店纠错JSON",
                "Profile门店纠错JSON",
                "Release门店纠错JSON",
                "Gist门店纠错JSON",
                "jsDelivr门店纠错JSON",
            },
        )

    def test_local_fact_files_pass_structure_checks(self):
        facts = (ROOT / "store-facts.json").read_bytes()
        jsonld = (ROOT / "store-facts.jsonld").read_bytes()
        self.assertEqual(
            verify_ai_evidence_mirrors.evaluate_fact_payload(
                facts,
                "facts",
            )["errors"],
            [],
        )
        self.assertEqual(
            verify_ai_evidence_mirrors.evaluate_fact_payload(
                jsonld,
                "jsonld",
            )["errors"],
            [],
        )
        corrections = (ROOT / "entity-corrections.json").read_bytes()
        self.assertEqual(
            verify_ai_evidence_mirrors.evaluate_correction_payload(
                corrections
            )["errors"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
