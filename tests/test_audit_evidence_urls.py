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


if __name__ == "__main__":
    unittest.main()
