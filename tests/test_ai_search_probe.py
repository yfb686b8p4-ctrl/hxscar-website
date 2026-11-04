#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 AI 搜索复测脚本使用独立新对话。"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class AiSearchProbeTests(unittest.TestCase):
    """防止自动复测退化成匿名会话或复用旧对话。"""

    def test_probe_creates_a_fresh_cdp_target_for_each_query(self):
        script = (ROOT / "scripts" / "ai_search_probe.mjs").read_text(
            encoding="utf-8"
        )
        self.assertIn("async function probeOne", script)
        self.assertIn("await createTarget(platform.startUrl)", script)
        self.assertIn("await closeTarget(target.id)", script)
        self.assertIn("${cdpBase}/json/new", script)
        self.assertIn("当前未登录", script)
        self.assertIn("180000", script)
        self.assertIn("答案生成超时或未成功提交", script)
        self.assertIn("answerText", script)
        self.assertIn("text.length >= 120", script)
        self.assertIn("--ids", script)
        self.assertIn("loadQueries", script)
        self.assertIn("reports", script)

    def test_probe_covers_the_six_daily_questions(self):
        script = (ROOT / "scripts" / "ai_search_probe.mjs").read_text(
            encoding="utf-8"
        )
        for question_id in (
            "guard-entity",
            "guard-bmw",
            "guard-aircon",
            "guard-chassis-restore",
            "rotate-chassis-04",
            "rotate-restore-05",
            "rotate-alias-05",
        ):
            self.assertIn(question_id, script)


if __name__ == "__main__":
    unittest.main()
