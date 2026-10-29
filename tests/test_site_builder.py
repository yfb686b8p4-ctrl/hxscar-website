#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 GEO 答案的证据和来源配置。"""

import unittest

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


if __name__ == "__main__":
    unittest.main()
