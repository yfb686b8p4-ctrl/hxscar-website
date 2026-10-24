#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""准备每日搜索抽样、汇总真实结果并生成异常优先日报。"""

import argparse
import csv
import json
import platform
import re
import subprocess
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "daily_probe_plan.json"
KEYWORDS_PATH = ROOT / "config" / "search_keywords.json"
PLATFORM_CONFIG_PATH = ROOT / "config" / "external_platforms.json"
STATUS_PATH = ROOT / "publishing" / "status.json"
AUDIT_PATH = ROOT / "reports" / "site-audit.json"
DAILY_DIR = ROOT / "reports" / "daily"
DEPLOY_ROOT = (
    Path.home() / "Library" / "Application Support" / "hxscar-weekly-deploy" / "repo"
)
LAUNCH_LABEL = "com.hxscar.weekly-deploy"
TZ = timezone(timedelta(hours=8))
SITE_URL = "https://yfb686b8p4-web.github.io/hxscar-website"
HTTP_CHECKS = [
    ("首页", "/", "华信松汽车"),
    ("FAQ", "/faq.html", "FAQPage"),
    ("维修案例", "/cases.html", "维修案例"),
    ("门店资料", "/store-profile.html", "同一实体门店"),
    ("服务专题", "/services/index.html", "服务专题"),
    ("车型专题", "/models/index.html", "车型维修"),
    ("robots", "/robots.txt", "Sitemap:"),
    ("sitemap", "/sitemap.xml", "store-profile.html"),
    ("llms", "/llms.txt", "门店实体关系"),
]
RESULT_COLUMNS = [
    "check_id",
    "platform",
    "query",
    "category",
    "mentioned",
    "identity_relation",
    "address_ok",
    "phone_ok",
    "hours_ok",
    "position",
    "cited_source",
    "sentiment",
    "answer_summary",
    "notes",
]
TRUE_VALUES = {"1", "true", "yes", "y", "是", "提到", "命中", "正确"}
FALSE_VALUES = {"0", "false", "no", "n", "否", "未提到", "未命中", "错误"}
NA_VALUES = {"", "-", "na", "n/a", "不适用", "无"}


def load_json(path):
    """读取 JSON 文件。"""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    """写入格式化 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run(command, cwd=None):
    """执行命令并返回输出，不因非零退出码抛错。"""
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def git_status(path):
    """读取 Git 分支、提交和工作区状态。"""
    if not (path / ".git").exists():
        return {
            "available": False,
            "path": str(path),
            "error": "未找到 Git 仓库",
        }
    status = run(["git", "status", "--porcelain", "--branch"], cwd=path)
    log = run(["git", "log", "-1", "--format=%h%x09%s"], cwd=path)
    lines = status["stdout"].splitlines()
    changes = lines[1:] if lines else []
    first = lines[0] if lines else ""
    branch_match = re.match(r"## ([^.\s]+)", first)
    return {
        "available": status["returncode"] == 0,
        "path": str(path),
        "branch": branch_match.group(1) if branch_match else "",
        "clean": not changes,
        "change_count": len(changes),
        "head": log["stdout"],
        "error": status["stderr"] or log["stderr"],
    }


def launch_agent_status():
    """读取 LaunchAgent 状态和最近退出码。"""
    if platform.system() != "Darwin":
        return {"available": False, "error": "当前系统不是 macOS"}
    result = run(["launchctl", "print", f"gui/{os_uid()}/{LAUNCH_LABEL}"])
    output = result["stdout"]
    exit_match = re.search(r"last exit code = (-?\d+)", output)
    hour_match = re.search(r'"Hour" => (\d+)', output)
    minute_match = re.search(r'"Minute" => (\d+)', output)
    weekday_match = re.search(r'"Weekday" => (\d+)', output)
    return {
        "available": result["returncode"] == 0,
        "loaded": result["returncode"] == 0,
        "state": (
            re.search(r"^\s*state = (.+)$", output, re.MULTILINE).group(1)
            if re.search(r"^\s*state = (.+)$", output, re.MULTILINE)
            else ""
        ),
        "last_exit_code": int(exit_match.group(1)) if exit_match else None,
        "schedule": {
            "weekday": int(weekday_match.group(1)) if weekday_match else None,
            "hour": int(hour_match.group(1)) if hour_match else None,
            "minute": int(minute_match.group(1)) if minute_match else None,
        },
        "error": result["stderr"],
    }


def os_uid():
    """返回当前用户 UID。"""
    return run(["id", "-u"])["stdout"] or "0"


def fetch_url(url, expected, timeout=15):
    """访问 URL，失败时尝试本机代理。"""
    attempts = [
        ("直连", None),
        ("本机代理", "http://127.0.0.1:7897"),
    ]
    errors = []
    for label, proxy in attempts:
        started = time.monotonic()
        try:
            if proxy:
                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler(
                        {"http": proxy, "https": proxy}
                    )
                )
            else:
                opener = urllib.request.build_opener()
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "HxscarDailyControl/1.0"},
            )
            with opener.open(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", "ignore")
                return {
                    "ok": 200 <= response.status < 400 and expected in body,
                    "status": response.status,
                    "marker": expected,
                    "via": label,
                    "seconds": round(time.monotonic() - started, 2),
                    "error": "",
                }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errors.append(f"{label}: {exc}")
    return {
        "ok": False,
        "status": None,
        "marker": expected,
        "via": "",
        "seconds": None,
        "error": "；".join(errors),
    }


def collect_status():
    """收集部署、定时任务、站点和平台状态。"""
    audit = load_json(AUDIT_PATH) if AUDIT_PATH.exists() else {}
    publishing = load_json(STATUS_PATH) if STATUS_PATH.exists() else {}
    platform_config = load_json(PLATFORM_CONFIG_PATH)
    stored_platforms = publishing.get("platforms", {})
    platforms = {}
    for item in platform_config["platforms"]:
        stored = stored_platforms.get(item["id"], {})
        platforms[item["id"]] = {
            "name": item["name"],
            "priority": item["priority"],
            "objective": item.get("objective", ""),
            "status": stored.get("status", "pending"),
            "url": stored.get("url", ""),
            "notes": stored.get("notes", ""),
            "updated_at": stored.get("updated_at", ""),
        }
    platform_values = list(platforms.values())
    counts = defaultdict(int)
    for item in platform_values:
        counts[item.get("status", "unknown")] += 1
    with ThreadPoolExecutor(max_workers=6) as executor:
        http_results = list(
            executor.map(
                lambda item: {
                    "name": item[0],
                    "path": item[1],
                    **fetch_url(SITE_URL + item[1], item[2]),
                },
                HTTP_CHECKS,
            )
        )
    return {
        "checked_at": datetime.now(TZ).isoformat(),
        "source_repo": git_status(ROOT),
        "deploy_repo": git_status(DEPLOY_ROOT),
        "launch_agent": launch_agent_status(),
        "site": {
            "url": SITE_URL,
            "http": http_results,
            "http_passed": sum(1 for item in http_results if item["ok"]),
            "http_total": len(http_results),
            "audit_passed": audit.get("passed"),
            "audit": audit.get("data_counts", {}),
        },
        "publishing": {
            "counts": dict(counts),
            "platforms": platforms,
        },
    }


def keyword_entries():
    """读取完整关键词池。"""
    return load_json(KEYWORDS_PATH)["keywords"]


def rotating_queries(day, excluded_ids):
    """按日期稳定轮换长尾关键词。"""
    plan = load_json(CONFIG_PATH)
    count = int(plan.get("rotating_keywords_per_day", 2))
    candidates = [
        item
        for item in keyword_entries()
        if item["id"] not in excluded_ids
    ]
    if not candidates:
        return []
    by_category = defaultdict(list)
    for item in candidates:
        by_category[item["category"]].append(item)
    categories = list(by_category)
    offset = day.toordinal() % len(categories)
    selected = []
    for step in range(min(count, len(categories))):
        category = categories[(offset + step) % len(categories)]
        category_items = by_category[category]
        item = category_items[
            (day.toordinal() + step) % len(category_items)
        ]
        selected.append(
            {
                "id": f"rotate-{item['id']}",
                "category": item["category"],
                "query": item["query"],
                "source_keyword_id": item["id"],
                "checks": ["mentioned", "position"],
                "rotating": True,
            }
        )
    return selected


def build_probe_plan(day):
    """按日生成护栏问题与轮换问题。"""
    config = load_json(CONFIG_PATH)
    excluded = {
        item["source_keyword_id"]
        for item in config["guardrails"]
        if item.get("source_keyword_id")
    }
    probes = [dict(item, rotating=False) for item in config["guardrails"]]
    probes.extend(rotating_queries(day, excluded))
    rows = []
    for item in probes:
        for platform_name in config["platforms"]:
            rows.append(
                {
                    "check_id": item["id"],
                    "platform": platform_name,
                    "query": item["query"],
                    "category": item["category"],
                    "rotating": item.get("rotating", False),
                    "checks": item.get("checks", []),
                    "mentioned": "",
                    "identity_relation": "",
                    "address_ok": "",
                    "phone_ok": "",
                    "hours_ok": "",
                    "position": "",
                    "cited_source": "",
                    "sentiment": "",
                    "answer_summary": "",
                    "notes": "",
                }
            )
    return {
        "date": day.isoformat(),
        "generated_at": datetime.now(TZ).isoformat(),
        "platforms": config["platforms"],
        "guardrails": [item for item in probes if not item.get("rotating")],
        "rotating": [item for item in probes if item.get("rotating")],
        "rows": rows,
        "weekly_full_check_due": day.weekday() == 0,
    }


def write_csv(path, rows, columns):
    """写出 UTF-8 CSV。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def prepare(day, force=False):
    """生成当天检测计划并附带系统状态。"""
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    plan_path = DAILY_DIR / f"{day.isoformat()}-plan.json"
    csv_path = DAILY_DIR / f"{day.isoformat()}-results.csv"
    if plan_path.exists() and not force:
        plan = load_json(plan_path)
        plan["status_snapshot"] = collect_status()
        write_json(plan_path, plan)
        if not csv_path.exists():
            write_csv(csv_path, plan["rows"], RESULT_COLUMNS)
    else:
        plan = build_probe_plan(day)
        plan["status_snapshot"] = collect_status()
        write_json(plan_path, plan)
        write_csv(csv_path, plan["rows"], RESULT_COLUMNS)
    print(
        json.dumps(
            {
                "date": day.isoformat(),
                "plan": str(plan_path.relative_to(ROOT)),
                "results_csv": str(csv_path.relative_to(ROOT)),
                "probe_count": len(plan["rows"]),
                "guardrails": len(plan["guardrails"]),
                "rotating": len(plan["rotating"]),
                "weekly_full_check_due": plan["weekly_full_check_due"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return plan


def parse_optional_bool(value):
    """解析 CSV 布尔列，空值返回 None。"""
    normalized = str(value or "").strip().lower()
    if normalized in NA_VALUES:
        return None
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"无法识别布尔值: {value}")


def normalize_relation(value, category):
    """统一实体关系判断值。"""
    normalized = str(value or "").strip().lower()
    aliases = {
        "正确": "correct",
        "是": "correct",
        "同一家": "correct",
        "部分正确": "partial",
        "疑似": "partial",
        "错误": "wrong",
        "不是": "wrong",
        "不同": "wrong",
        "不适用": "not_applicable",
        "无": "not_applicable",
        "na": "not_applicable",
    }
    normalized = aliases.get(normalized, normalized)
    if not normalized:
        return "pending" if "门店身份" in category else "not_applicable"
    return normalized


def parse_results(path, plan):
    """将填写后的 CSV 合并回检测计划。"""
    raw_rows = {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            raw_rows[(row["check_id"].strip(), row["platform"].strip())] = row
    records = []
    for planned in plan["rows"]:
        key = (planned["check_id"], planned["platform"])
        row = raw_rows.get(key, {})
        mentioned = parse_optional_bool(row.get("mentioned", ""))
        status = "completed" if mentioned is not None else "pending"
        record = {
            "check_id": planned["check_id"],
            "platform": planned["platform"],
            "query": planned["query"],
            "category": planned["category"],
            "rotating": planned.get("rotating", False),
            "status": status,
            "mentioned": mentioned,
            "identity_relation": normalize_relation(
                row.get("identity_relation", ""), planned["category"]
            ),
            "address_ok": parse_optional_bool(row.get("address_ok", "")),
            "phone_ok": parse_optional_bool(row.get("phone_ok", "")),
            "hours_ok": parse_optional_bool(row.get("hours_ok", "")),
            "position": (
                int(row["position"])
                if str(row.get("position", "")).strip().isdigit()
                else None
            ),
            "cited_source": (row.get("cited_source") or "").strip(),
            "sentiment": (row.get("sentiment") or "").strip(),
            "answer_summary": (row.get("answer_summary") or "").strip(),
            "notes": (row.get("notes") or "").strip(),
        }
        record["effective_hit"] = evaluate_effective_hit(record)
        records.append(record)
    return records


def evaluate_effective_hit(record):
    """判断一条结果是否真正达到搜索目标。"""
    if record["status"] != "completed" or not record["mentioned"]:
        return False
    if "门店身份" not in record["category"]:
        return True
    return (
        record["identity_relation"] == "correct"
        and record["address_ok"] is True
        and record["phone_ok"] is True
        and record["hours_ok"] is True
    )


def ratio(part, total):
    """安全计算百分比。"""
    return round(part / total * 100, 1) if total else 0.0


def calculate_metrics(records):
    """计算每日有效命中与关键资料正确率。"""
    completed = [item for item in records if item["status"] == "completed"]
    identity = [
        item for item in completed if "门店身份" in item["category"]
    ]
    services = [
        item for item in completed if "门店身份" not in item["category"]
    ]
    return {
        "total": len(records),
        "completed": len(completed),
        "pending": len(records) - len(completed),
        "mentioned": sum(1 for item in completed if item["mentioned"]),
        "effective_hits": sum(1 for item in completed if item["effective_hit"]),
        "effective_hit_rate": ratio(
            sum(1 for item in completed if item["effective_hit"]),
            len(completed),
        ),
        "entity_completed": len(identity),
        "entity_correct": sum(
            1 for item in identity if item["identity_relation"] == "correct"
        ),
        "entity_correct_rate": ratio(
            sum(
                1
                for item in identity
                if item["identity_relation"] == "correct"
            ),
            len(identity),
        ),
        "full_info_correct": sum(
            1
            for item in identity
            if item["address_ok"] is True
            and item["phone_ok"] is True
            and item["hours_ok"] is True
        ),
        "full_info_correct_rate": ratio(
            sum(
                1
                for item in identity
                if item["address_ok"] is True
                and item["phone_ok"] is True
                and item["hours_ok"] is True
            ),
            len(identity),
        ),
        "service_completed": len(services),
        "service_hits": sum(1 for item in services if item["mentioned"]),
        "service_hit_rate": ratio(
            sum(1 for item in services if item["mentioned"]),
            len(services),
        ),
    }


def previous_summary(today):
    """读取今天之前最近一份日报汇总。"""
    candidates = []
    for path in DAILY_DIR.glob("20??-??-??.json"):
        try:
            item_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if item_date < today:
            candidates.append((item_date, path))
    if not candidates:
        return None
    return load_json(max(candidates)[1])


def compare_results(records, previous):
    """比较与上一份日报相比的修复、回归和指标变化。"""
    if not previous:
        return {"previous_date": None, "metric_changes": {}, "fixed": [], "new_errors": []}
    old_records = {
        (item["check_id"], item["platform"]): item
        for item in previous.get("records", [])
        if item.get("status") == "completed"
    }
    new_records = {
        (item["check_id"], item["platform"]): item
        for item in records
        if item.get("status") == "completed"
    }
    fixed = []
    new_errors = []
    for key in sorted(set(old_records) & set(new_records)):
        before = old_records[key]
        after = new_records[key]
        label = f"{key[1]}｜{after['query']}"
        if not before.get("effective_hit") and after.get("effective_hit"):
            fixed.append(label)
        elif before.get("effective_hit") and not after.get("effective_hit"):
            new_errors.append(label)
    stable_records = [
        item for item in records if not item.get("rotating", False)
    ]
    metrics = calculate_metrics(stable_records)
    previous_metrics = previous.get("guardrail_metrics") or previous.get(
        "metrics", {}
    )
    if not previous_metrics.get("completed"):
        return {
            "previous_date": previous.get("date"),
            "comparable": False,
            "metric_changes": {},
            "fixed": [],
            "new_errors": [],
        }
    changes = {}
    for key, value in metrics.items():
        if key in {"total", "completed", "pending", "mentioned", "effective_hits", "entity_completed", "entity_correct", "full_info_correct", "service_completed", "service_hits"}:
            continue
        changes[key] = round(value - float(previous_metrics.get(key, 0)), 1)
    return {
        "previous_date": previous.get("date"),
        "comparable": True,
        "metric_changes": changes,
        "fixed": fixed,
        "new_errors": new_errors,
    }


def failed_records(records):
    """返回已完成但未达到目标的记录。"""
    return [
        item
        for item in records
        if item["status"] == "completed" and not item["effective_hit"]
    ]


def build_tasks(records, status=None):
    """根据失败结果生成去重后的可执行任务。"""
    tasks = defaultdict(
        lambda: {
            "priority": "P1",
            "action": "",
            "category": "",
            "platforms": set(),
            "sources": set(),
            "check_ids": set(),
            "requires_confirmation": False,
        }
    )
    for item in failed_records(records):
        if "门店身份" in item["category"] and item["identity_relation"] != "correct":
            key = "entity-identity"
            task = tasks[key]
            task.update(
                {
                    "priority": "P0",
                    "action": "统一门店实体证据：明确同一实体门店、同一地址、同一运营团队，并区分其他同名分店。",
                    "category": item["category"],
                    "requires_confirmation": True,
                }
            )
        elif "门店身份" in item["category"]:
            field_labels = []
            if item["address_ok"] is not True:
                field_labels.append("地址")
            if item["phone_ok"] is not True:
                field_labels.append("电话")
            if item["hours_ok"] is not True:
                field_labels.append("营业时间")
            key = "identity-fields-" + "-".join(field_labels or ["资料"])
            task = tasks[key]
            task.update(
                {
                    "priority": "P0",
                    "action": f"修正门店{'、'.join(field_labels or ['基础资料'])}，并核验引用来源。",
                    "category": item["category"],
                    "requires_confirmation": True,
                }
            )
        else:
            key = "service-" + item["category"]
            task = tasks[key]
            task.update(
                {
                    "priority": "P1",
                    "action": f"补充“{item['category']}”真实案例和可引用内容，使本店进入推荐候选。",
                    "category": item["category"],
                    "requires_confirmation": False,
                }
            )
        task["platforms"].add(item["platform"])
        task["check_ids"].add(item["check_id"])
        if item.get("cited_source"):
            task["sources"].add(item["cited_source"])
    platform_status = (status or {}).get("publishing", {}).get(
        "platforms", {}
    )
    for platform_id, item in platform_status.items():
        state = item.get("status", "unknown")
        note = item.get("notes", "").strip()
        needs_followup = any(
            marker in note for marker in ("需", "待", "当前简介")
        )
        if state in {"published", "completed"} and not needs_followup:
            continue
        suffix = "-followup" if state in {"published", "completed"} else ""
        key = f"platform-{platform_id}{suffix}"
        priority = item.get("priority") or (
            "P0" if platform_id == "tencent-map" else "P1"
        )
        tasks[key].update(
            {
                "priority": priority,
                "action": note
                or item.get("objective")
                or f"完成 {platform_id} 的门店资料更新并回填链接。",
                "category": "站外权威资料",
                "requires_confirmation": True,
            }
        )
        tasks[key]["platforms"].add(item.get("name") or platform_id)
        tasks[key]["sources"].add("publishing/status.json")
    output = []
    for key, value in tasks.items():
        output.append(
            {
                "id": key,
                **value,
                "platforms": sorted(value["platforms"]),
                "sources": sorted(value["sources"]),
                "check_ids": sorted(value["check_ids"]),
            }
        )
    return sorted(output, key=lambda item: (item["priority"], item["id"]))


def compare_tasks(tasks, previous):
    """比较新增、关闭和持续待办。"""
    current_ids = {item["id"] for item in tasks}
    previous_tasks = (previous or {}).get("tasks", [])
    previous_ids = {item["id"] for item in previous_tasks}
    return {
        "new": sorted(current_ids - previous_ids),
        "closed": sorted(previous_ids - current_ids),
        "persistent_count": len(current_ids & previous_ids),
    }


def render_markdown(summary):
    """生成异常优先的每日 Markdown 简报。"""
    metrics = summary["metrics"]
    guardrails = summary.get("guardrail_metrics", metrics)
    rotating = summary.get("rotating_metrics", calculate_metrics([]))
    changes = summary["changes"]
    status = summary["status"]
    def display_rate(value, sample_count):
        return f"{value}%" if sample_count else "待检测"

    if not metrics["completed"]:
        headline = "基础状态检查完成，搜索结果尚未实测。"
    else:
        headline = (
            f"已完成 {metrics['completed']} 项搜索检查，"
            f"有效命中 {metrics['effective_hits']} 项。"
        )
    lines = [
        f"# AI 搜索每日效果简报｜{summary['date']}",
        "",
        f"- 生成时间：{summary['generated_at']}",
        f"- 今日结论：{headline}",
        f"- 完成检查：{metrics['completed']}/{metrics['total']}，待补测 {metrics['pending']}",
        f"- 护栏有效命中率：{display_rate(guardrails['effective_hit_rate'], guardrails['completed'])}",
        f"- 门店实体关系正确率：{display_rate(guardrails['entity_correct_rate'], guardrails['entity_completed'])}",
        f"- 地址、电话、营业时间完整正确率：{display_rate(guardrails['full_info_correct_rate'], guardrails['entity_completed'])}",
        f"- 服务推荐命中率：{display_rate(guardrails['service_hit_rate'], guardrails['service_completed'])}",
        f"- 轮换探测：{rotating['completed']}/{rotating['total']} 完成，"
        f"提及 {rotating['mentioned']} 项",
        "",
        "## 与上一份日报相比",
        "",
    ]
    previous_date = changes.get("previous_date")
    if not previous_date:
        lines.append("- 暂无上一份日报，今天作为基线。")
    elif not changes.get("comparable", True):
        lines.append(
            f"- 对比日期：{previous_date}，但昨天没有已完成的护栏结果；"
            "今天作为首个可比基线。"
        )
    else:
        delta = changes.get("metric_changes", {})
        lines.append(f"- 对比日期：{previous_date}")
        lines.append(
            f"- 有效命中率变化：{delta.get('effective_hit_rate', 0):+} 个百分点"
        )
        lines.append(
            f"- 实体关系正确率变化：{delta.get('entity_correct_rate', 0):+} 个百分点"
        )
        lines.append(
            f"- 完整资料正确率变化：{delta.get('full_info_correct_rate', 0):+} 个百分点"
        )
    lines.extend(["", "## 今天确认改善", ""])
    fixed = changes.get("fixed", [])
    lines.extend(f"- {item}" for item in fixed) if fixed else lines.append("- 无")
    lines.extend(["", "## 新增或仍然错误", ""])
    new_errors = changes.get("new_errors", [])
    if new_errors:
        lines.extend(f"- 新增错误：{item}" for item in new_errors)
    failures = failed_records(summary["records"])
    if failures:
        for item in failures:
            details = []
            if item["identity_relation"] not in {"not_applicable", "pending"}:
                details.append(f"实体={item['identity_relation']}")
            for field, label in (
                ("address_ok", "地址"),
                ("phone_ok", "电话"),
                ("hours_ok", "营业时间"),
            ):
                if item[field] is False:
                    details.append(f"{label}=错误")
            if not item["mentioned"]:
                details.append("未提及")
            line = (
                f"- {item['platform']}｜{item['query']}："
                f"{'，'.join(details) or '未达到有效命中'}"
            )
            if item["notes"]:
                line += f"｜{item['notes']}"
            lines.append(line)
    else:
        lines.append("- 无")
    lines.extend(["", "## 运行状态", ""])
    launch = status.get("launch_agent", {})
    site = status.get("site", {})
    lines.extend(
        [
            f"- 线上页面：{site.get('http_passed', 0)}/{site.get('http_total', 0)} 通过",
            f"- 最近站点审计：{'通过' if site.get('audit_passed') else '未通过或缺失'}",
            f"- 自动部署：{'已加载' if launch.get('loaded') else '未加载'}，"
            f"最近退出码 {launch.get('last_exit_code')}",
            f"- 源仓库：{status.get('source_repo', {}).get('head', '未知')}，"
            f"{'干净' if status.get('source_repo', {}).get('clean') else '有未提交改动'}",
            f"- 部署副本：{status.get('deploy_repo', {}).get('head', '未知')}，"
            f"{'干净' if status.get('deploy_repo', {}).get('clean') else '有未提交改动'}",
        ]
    )
    lines.extend(["", "## 待执行任务", ""])
    task_changes = summary.get("task_changes", {})
    new_ids = set(task_changes.get("new", []))
    new_tasks = [
        task for task in summary["tasks"] if task["id"] in new_ids
    ]
    if new_tasks:
        for task in new_tasks:
            confirmation = "，需用户确认" if task["requires_confirmation"] else ""
            lines.append(
                f"- {task['priority']}｜{task['action']}｜"
                f"平台：{'、'.join(task['platforms'])}"
                f"{confirmation}"
            )
    elif not task_changes.get("persistent_count"):
        lines.append("- 无")
    if task_changes.get("persistent_count"):
        lines.append(
            f"- 持续待办：{task_changes['persistent_count']} 项，"
            "详见 `reports/daily/latest-tasks.json`"
        )
    if task_changes.get("closed"):
        lines.append(
            f"- 已关闭：{'、'.join(task_changes['closed'])}"
        )
    errors = [
        item
        for item in site.get("http", [])
        if not item.get("ok")
    ]
    lines.extend(["", "## 运行异常", ""])
    if errors:
        for item in errors:
            lines.append(
                f"- {item['name']}：{item.get('status') or '失败'}"
                f" {item.get('error', '')}".rstrip()
            )
    else:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def finalize(day, results_path):
    """导入当天实测结果并生成日报、对比和任务。"""
    plan_path = DAILY_DIR / f"{day.isoformat()}-plan.json"
    if not plan_path.exists():
        raise FileNotFoundError(f"缺少检测计划: {plan_path}")
    plan = load_json(plan_path)
    records = parse_results(results_path, plan)
    metrics = calculate_metrics(records)
    guardrail_metrics = calculate_metrics(
        [item for item in records if not item.get("rotating", False)]
    )
    rotating_metrics = calculate_metrics(
        [item for item in records if item.get("rotating", False)]
    )
    previous = previous_summary(day)
    changes = compare_results(records, previous)
    status = plan.get("status_snapshot") or collect_status()
    tasks = build_tasks(records, status)
    summary = {
        "version": 1,
        "date": day.isoformat(),
        "generated_at": datetime.now(TZ).isoformat(),
        "metrics": metrics,
        "guardrail_metrics": guardrail_metrics,
        "rotating_metrics": rotating_metrics,
        "changes": changes,
        "status": status,
        "tasks": tasks,
        "task_changes": compare_tasks(tasks, previous),
        "records": records,
    }
    write_json(DAILY_DIR / f"{day.isoformat()}.json", summary)
    write_json(DAILY_DIR / "latest.json", summary)
    write_json(DAILY_DIR / "latest-tasks.json", summary["tasks"])
    write_csv(DAILY_DIR / f"{day.isoformat()}-results.csv", records, RESULT_COLUMNS)
    markdown = render_markdown(summary)
    (DAILY_DIR / f"{day.isoformat()}.md").write_text(
        markdown, encoding="utf-8"
    )
    (DAILY_DIR / "latest.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"日报：{DAILY_DIR / f'{day.isoformat()}.md'}")
    print(f"待办：{DAILY_DIR / 'latest-tasks.json'}")
    return summary


def parse_date(value):
    """解析命令行日期。"""
    return date.fromisoformat(value) if value else datetime.now(TZ).date()


def main():
    parser = argparse.ArgumentParser(description="每日 AI 搜索检查控制台")
    parser.add_argument("--prepare", action="store_true", help="生成当天检测计划")
    parser.add_argument("--finalize", help="导入填写的 CSV 并生成日报")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD")
    parser.add_argument("--force", action="store_true", help="覆盖当天计划")
    args = parser.parse_args()
    day = parse_date(args.date)
    if args.finalize:
        finalize(day, Path(args.finalize))
    else:
        prepare(day, force=args.force)


if __name__ == "__main__":
    main()
