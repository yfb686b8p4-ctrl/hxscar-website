#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证机器证据 URL 审计器。"""

import unittest

from scripts import audit_evidence_urls


class AuditEvidenceUrlsTests(unittest.TestCase):
    """确保 URL 去重、规范化与成功状态判断正确。"""

    def test_extract_urls_deduplicates_and_cleans_punctuation(self):
        urls = audit_evidence_urls.extract_urls(
            [
                '{"url":"https://example.com/a"},',
                "https://example.com/a；https://example.com/b。",
            ]
        )
        self.assertEqual(
            urls,
            [
                "https://example.com/a",
                "https://example.com/b",
            ],
        )

    def test_success_accepts_2xx_and_redirects(self):
        for status in (200, 206, 301, 308):
            self.assertTrue(audit_evidence_urls.is_success(status))
        for status in (0, 400, 403, 404, 500):
            self.assertFalse(audit_evidence_urls.is_success(status))

    def test_platform_blocks_are_separate_from_broken_links(self):
        for status in (401, 403, 405, 429):
            self.assertTrue(audit_evidence_urls.is_blocked(status))
        for status in (0, 200, 206, 301, 404, 500):
            self.assertFalse(audit_evidence_urls.is_blocked(status))
        self.assertTrue(
            audit_evidence_urls.is_blocked(
                404,
                "https://web.archive.org/web/1/example",
            )
        )
        self.assertTrue(
            audit_evidence_urls.is_blocked(
                0,
                "https://r.jina.ai/https://example.com",
            )
        )


if __name__ == "__main__":
    unittest.main()
