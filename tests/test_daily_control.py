#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日搜索控制台的纯逻辑测试。"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import daily_control


def record(**overrides):
    """构造测试记录。"""
    data = {
        "check_id": "guard-entity",
        "platform": "元宝",
        "query": "门店关系",
        "category": "门店身份",
        "status": "completed",
        "mentioned": True,
        "identity_relation": "correct",
        "address_ok": True,
        "phone_ok": True,
        "hours_ok": True,
        "effective_hit": True,
        "position": 1,
        "cited_source": "",
    }
    data.update(overrides)
    return data


class DailyControlTests(unittest.TestCase):
    """验证每日命中、对比和任务生成。"""

    def test_generated_report_files_do_not_mark_source_dirty(self):
        """日报生成物不应让源码状态被误报为未提交代码。"""
        prefixes = daily_control.GENERATED_REPORT_PREFIXES
        self.assertTrue(
            " M reports/daily/latest.json"[3:].startswith(prefixes)
        )
        self.assertTrue(
            " M reports/final-summary-2026-11-01.md"[3:].startswith(prefixes)
        )
        self.assertTrue(
            " M reports/optimization-2026-11-01.md"[3:].startswith(prefixes)
        )
        self.assertTrue(
            " M reports/recheck-2026-11-01.json"[3:].startswith(prefixes)
        )
        self.assertFalse(
            " M scripts/site_builder.py"[3:].startswith(prefixes)
        )

    def test_bool_parser(self):
        self.assertIs(daily_control.parse_optional_bool("是"), True)
        self.assertIs(daily_control.parse_optional_bool("错误"), False)
        self.assertIsNone(daily_control.parse_optional_bool(""))

    def test_curl_response_parser_requires_marker_text(self):
        parsed = daily_control.parse_curl_response(
            "页面包含华信松汽车\n__HXSCAR_STATUS__200",
            "华信松汽车",
        )
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["status"], 200)
        self.assertIn("华信松汽车", parsed["body"])

        missing = daily_control.parse_curl_response(
            "页面内容\n__HXSCAR_STATUS__200",
            "指定标记",
        )
        self.assertFalse(missing["ok"])

    def test_large_assets_use_network_tolerant_timeouts(self):
        """大图片和 PDF 不应沿用短页面超时，避免慢网误报线上故障。"""
        checks = {item[1]: item for item in daily_control.HTTP_CHECKS}
        self.assertEqual(
            checks["/assets/store-banner.jpg"][3],
            60,
        )
        self.assertEqual(
            checks["/assets/store-banner-960.jpg"][3],
            30,
        )
        self.assertEqual(
            checks["/feed.xml"][3],
            45,
        )
        self.assertEqual(
            checks[
                "/downloads/huaxinsong-store-facts-2026-10-31.pdf"
            ][3],
            90,
        )

    def test_check_url_supports_profile_mirror_absolute_urls(self):
        """主站相对路径与 Profile 绝对 URL 必须都能正确解析。"""
        self.assertEqual(
            daily_control.resolve_check_url("/faq.html"),
            daily_control.SITE_URL + "/faq.html",
        )
        profile_url = (
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/llms.txt"
        )
        self.assertEqual(
            daily_control.resolve_check_url(profile_url),
            profile_url,
        )
        checks = {item[1]: item for item in daily_control.HTTP_CHECKS}
        self.assertIn(profile_url, checks)
        self.assertIn("/douyin-video-evidence.json", checks)
        self.assertEqual(
            checks[
                "https://yfb686b8p4-web.github.io/yfb686b8p4-web/answers.html"
            ][2],
            "九个直接答案",
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "image-sitemap.xml",
            checks,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "assets/store-banner.jpg",
            checks,
        )
        self.assertIn(
            "https://yfb686b8p4-web.github.io/yfb686b8p4-web/"
            "entity-corrections.json",
            checks,
        )

    def test_checks_cover_release_and_gist_qa_mirrors(self):
        """每日检查必须覆盖 Release、Gist 与 jsDelivr 问答镜像。"""
        checks = {item[1] for item in daily_control.HTTP_CHECKS}
        self.assertIn(
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "qa-evidence.jsonl?v=20261101-v5",
            checks,
        )
        self.assertIn(
            "https://gist.githubusercontent.com/yfb686b8p4-web/"
            "7923ef0b18ffbcce04a8b6758254a06b/raw/ENTITY_FACTS.md",
            checks,
        )
        self.assertIn(
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/"
            "hxscar-website@ai-evidence-cdn-2026-11-01-v12/"
            "qa-evidence.jsonl",
            checks,
        )
        self.assertIn(
            "https://cdn.jsdelivr.net/gh/yfb686b8p4-web/"
            "hxscar-website@ai-evidence-cdn-2026-11-01-v12/"
            "store-facts.json",
            checks,
        )
        self.assertIn(
            "/downloads/entity-facts-2026-11-01.md",
            checks,
        )
        self.assertIn(
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "entity-facts.md?v=20261101-entity-facts",
            checks,
        )
        self.assertIn(
            "https://gist.githubusercontent.com/yfb686b8p4-web/"
            "7923ef0b18ffbcce04a8b6758254a06b/raw/"
            "qa-evidence.jsonl?v=20261101-cdn-v5",
            checks,
        )
        self.assertIn(
            "https://github.com/yfb686b8p4-web/hxscar-website/"
            "releases/download/ai-evidence-2026-11-01/"
            "entity-corrections.json?v=20261101-v5",
            checks,
        )

    def test_effective_hit_requires_complete_identity(self):
        self.assertTrue(daily_control.evaluate_effective_hit(record()))
        self.assertFalse(
            daily_control.evaluate_effective_hit(record(phone_ok=False))
        )
        self.assertFalse(
            daily_control.evaluate_effective_hit(
                record(identity_relation="partial")
            )
        )

    def test_service_mention_is_effective(self):
        item = record(
            check_id="guard-bmw",
            category="宝马与豪车",
            identity_relation="not_applicable",
            address_ok=None,
            phone_ok=None,
            hours_ok=None,
        )
        self.assertTrue(daily_control.evaluate_effective_hit(item))

    def test_metrics(self):
        metrics = daily_control.calculate_metrics(
            [
                record(cited_source="官网"),
                record(
                    check_id="guard-aircon",
                    category="空调诊断维修",
                    identity_relation="not_applicable",
                    address_ok=None,
                    phone_ok=None,
                    hours_ok=None,
                ),
                record(
                    check_id="guard-chassis",
                    category="底盘与老车整备",
                    mentioned=False,
                    identity_relation="not_applicable",
                    address_ok=None,
                    phone_ok=None,
                    hours_ok=None,
                    effective_hit=False,
                ),
                record(
                    check_id="guard-bmw",
                    category="宝马与豪车",
                    identity_relation="not_applicable",
                    address_ok=None,
                    phone_ok=None,
                    hours_ok=None,
                    position=3,
                ),
            ]
        )
        self.assertEqual(metrics["completed"], 4)
        self.assertEqual(metrics["effective_hits"], 3)
        self.assertEqual(metrics["entity_correct_rate"], 100.0)
        self.assertEqual(metrics["service_hit_rate"], 66.7)
        self.assertEqual(metrics["citation_rate"], 25.0)
        self.assertEqual(metrics["service_top1_rate"], 33.3)
        self.assertEqual(metrics["service_top3_rate"], 66.7)

    def test_metrics_reports_excluded_sessions_separately(self):
        metrics = daily_control.calculate_metrics(
            [
                record(),
                record(
                    status="excluded",
                    mentioned=False,
                    effective_hit=False,
                ),
                record(status="pending", mentioned=None, effective_hit=False),
            ]
        )
        self.assertEqual(metrics["completed"], 1)
        self.assertEqual(metrics["excluded"], 1)
        self.assertEqual(metrics["pending"], 1)

    def test_comparison_detects_fixed_and_regression(self):
        old = [
            record(effective_hit=False, phone_ok=False),
            record(check_id="guard-bmw", category="宝马与豪车", effective_hit=True),
        ]
        new = [
            record(effective_hit=True),
            record(
                check_id="guard-bmw",
                category="宝马与豪车",
                mentioned=False,
                effective_hit=False,
            ),
        ]
        changes = daily_control.compare_results(
            new,
            {
                "date": "2026-10-22",
                "records": old,
                "metrics": daily_control.calculate_metrics(old),
            },
        )
        self.assertEqual(len(changes["fixed"]), 1)
        self.assertEqual(len(changes["new_errors"]), 1)

    def test_pending_baseline_is_not_compared_as_zero(self):
        changes = daily_control.compare_results(
            [record()],
            {
                "date": "2026-10-23",
                "records": [],
                "metrics": daily_control.calculate_metrics([]),
            },
        )
        self.assertFalse(changes["comparable"])
        self.assertEqual(changes["metric_changes"], {})

    def test_pending_current_results_are_not_reported_as_regression(self):
        changes = daily_control.compare_results(
            [],
            {
                "date": "2026-10-24",
                "records": [record()],
                "guardrail_metrics": daily_control.calculate_metrics([record()]),
            },
        )
        self.assertFalse(changes["comparable"])
        self.assertEqual(changes["reason"], "current_pending")
        self.assertEqual(changes["metric_changes"], {})

    def test_tasks_are_grouped(self):
        tasks = daily_control.build_tasks(
            [
                record(identity_relation="wrong", effective_hit=False),
                record(
                    check_id="guard-aircon",
                    category="空调诊断维修",
                    mentioned=False,
                    identity_relation="not_applicable",
                    address_ok=None,
                    phone_ok=None,
                    hours_ok=None,
                    effective_hit=False,
                ),
            ]
        )
        ids = {item["id"] for item in tasks}
        self.assertIn("entity-identity", ids)
        self.assertIn("service-空调诊断维修", ids)

    def test_blocked_platform_creates_task(self):
        tasks = daily_control.build_tasks(
            [],
            {
                "publishing": {
                    "platforms": {
                        "tencent-map": {
                            "status": "blocked",
                            "notes": "等待扫码入驻",
                        }
                    }
                }
            },
        )
        self.assertEqual(tasks[0]["id"], "platform-tencent-map")
        self.assertEqual(tasks[0]["priority"], "P0")
        self.assertTrue(tasks[0]["requires_confirmation"])

    def test_published_platform_with_followup_creates_task(self):
        tasks = daily_control.build_tasks(
            [],
            {
                "publishing": {
                    "platforms": {
                        "douyin": {
                            "name": "抖音生活服务",
                            "priority": "P0",
                            "status": "published",
                            "notes": "当前简介需补齐地址和营业时间",
                        }
                    }
                }
            },
        )
        self.assertEqual(tasks[0]["id"], "platform-douyin-followup")

    def test_task_comparison(self):
        changes = daily_control.compare_tasks(
            [{"id": "a"}, {"id": "b"}],
            {"tasks": [{"id": "b"}, {"id": "c"}]},
        )
        self.assertEqual(changes["new"], ["a"])
        self.assertEqual(changes["closed"], ["c"])
        self.assertEqual(changes["persistent_count"], 1)

    def test_incomplete_checks_prevent_task_closure(self):
        changes = daily_control.compare_tasks(
            [],
            {
                "tasks": [
                    {
                        "id": "entity-identity",
                        "check_ids": ["guard-entity"],
                    }
                ]
            },
            records=[
                {
                    "status": "pending",
                    "check_id": "guard-entity",
                }
            ],
        )
        self.assertEqual(changes["closed"], [])
        self.assertEqual(changes["deferred"], ["entity-identity"])

    def test_contextual_session_is_excluded_from_metrics(self):
        plan = {
            "rows": [
                {
                    "check_id": "guard-aircon",
                    "platform": "元宝",
                    "session_mode": "fresh_required",
                    "query": "空调问题",
                    "category": "空调诊断维修",
                    "rotating": False,
                }
            ]
        }
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "results.csv"
            path.write_text(
                "check_id,platform,session_mode,query,category,"
                "mentioned,identity_relation,address_ok,phone_ok,"
                "hours_ok,position,cited_source,sentiment,"
                "answer_summary,notes\n"
                "guard-aircon,元宝,contextual,空调问题,空调诊断维修,"
                "False,not_applicable,,,,20篇资料,中性,回答,"
                "测试；会话未使用全新对话，结果不计入指标\n",
                encoding="utf-8",
            )
            records = daily_control.parse_results(path, plan)
        self.assertEqual(records[0]["status"], "excluded")
        self.assertFalse(records[0]["effective_hit"])
        self.assertEqual(
            records[0]["notes"].count("会话未使用全新对话，结果不计入指标"),
            1,
        )

    def test_parse_results_keeps_unfilled_rows_pending(self):
        plan = {
            "rows": [
                {
                    "check_id": "guard-entity",
                    "platform": "元宝",
                    "query": "门店关系",
                    "category": "门店身份",
                    "rotating": False,
                },
                {
                    "check_id": "guard-aircon",
                    "platform": "豆包",
                    "query": "空调维修",
                    "category": "空调诊断维修",
                    "rotating": False,
                },
            ]
        }
        with TemporaryDirectory() as directory:
            path = Path(directory) / "results.csv"
            path.write_text(
                "check_id,platform,query,category,mentioned,identity_relation,"
                "address_ok,phone_ok,hours_ok,position,cited_source,"
                "sentiment,answer_summary,notes\n"
                "guard-entity,元宝,门店关系,门店身份,是,正确,是,是,是,1,官网,"
                "positive,完整,无\n",
                encoding="utf-8",
            )
            records = daily_control.parse_results(path, plan)
        self.assertTrue(records[0]["effective_hit"])
        self.assertEqual(records[1]["status"], "pending")

    def test_pending_report_does_not_show_zero_percent(self):
        markdown = daily_control.render_markdown(
            {
                "date": "2026-10-23",
                "generated_at": "2026-10-23T09:00:00+08:00",
                "metrics": daily_control.calculate_metrics([]),
                "changes": {
                    "previous_date": None,
                    "metric_changes": {},
                    "fixed": [],
                    "new_errors": [],
                },
                "status": {
                    "launch_agent": {},
                    "site": {"http": []},
                    "source_repo": {},
                    "deploy_repo": {},
                },
                "tasks": [],
                "records": [],
            }
        )
        self.assertIn("待检测", markdown)
        self.assertIn("最近退出码 暂无记录", markdown)
        self.assertNotIn("最近退出码 None", markdown)

    def test_service_rates_use_all_records_not_guardrail_subset(self):
        """日报 Top1/Top3 必须使用全量服务样本，避免与最终汇总口径冲突。"""
        metrics = daily_control.calculate_metrics([])
        metrics.update(
            {
                "completed": 12,
                "total": 12,
                "service_completed": 10,
                "service_hits": 4,
                "service_hit_rate": 40.0,
                "service_top1": 4,
                "service_top1_rate": 40.0,
                "service_top3": 4,
                "service_top3_rate": 40.0,
            }
        )
        guardrails = dict(metrics)
        guardrails.update(
            {
                "completed": 8,
                "total": 8,
                "service_completed": 6,
                "service_hits": 3,
                "service_hit_rate": 50.0,
                "service_top1_rate": 50.0,
                "service_top3_rate": 50.0,
            }
        )
        markdown = daily_control.render_markdown(
            {
                "date": "2026-11-01",
                "generated_at": "2026-11-01T09:00:00+08:00",
                "metrics": metrics,
                "guardrail_metrics": guardrails,
                "changes": {
                    "previous_date": None,
                    "metric_changes": {},
                    "fixed": [],
                    "new_errors": [],
                },
                "status": {
                    "launch_agent": {},
                    "site": {"http": []},
                    "source_repo": {},
                    "deploy_repo": {},
                },
                "tasks": [],
                "records": [],
            }
        )
        self.assertIn("- 服务推荐命中率：40.0%", markdown)
        self.assertIn("- 服务推荐 Top1 率：40.0%", markdown)
        self.assertIn("- 服务推荐 Top3 率：40.0%", markdown)


if __name__ == "__main__":
    unittest.main()
