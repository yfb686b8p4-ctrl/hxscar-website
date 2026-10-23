#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立并汇总每周 AI 搜索可见性记录。"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "search_keywords.json"
HISTORY_DIR = ROOT / "reports" / "rank-history"
TZ = timezone(timedelta(hours=8))


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


def current_snapshot_path():
    """返回当天排名快照路径。"""
    today = datetime.now(TZ).date().isoformat()
    return HISTORY_DIR / f"{today}.json"


def build_empty_results(config):
    """创建关键词与平台的完整待测矩阵。"""
    results = {}
    for item in config["keywords"]:
        results[item["id"]] = {
            "query": item["query"],
            "category": item["category"],
            "intent": item["intent"],
            "platforms": {
                platform: {
                    "status": "pending",
                    "mentioned": None,
                    "matched_aliases": [],
                    "position": None,
                    "cited_source": "",
                    "sentiment": "",
                    "notes": "",
                }
                for platform in config["platforms"]
            },
        }
    return results


def init_snapshot():
    """初始化当天快照，不覆盖已经记录的结果。"""
    config = load_json(CONFIG_PATH)
    path = current_snapshot_path()
    existing = load_json(path) if path.exists() else {}
    results = existing.get("results", {})
    defaults = build_empty_results(config)
    changed = not bool(existing)

    for keyword_id, default in defaults.items():
        if keyword_id not in results:
            results[keyword_id] = default
            changed = True
        current = results[keyword_id]
        current.update(
            {
                "query": default["query"],
                "category": default["category"],
                "intent": default["intent"],
            }
        )
        platforms = current.setdefault("platforms", {})
        for platform in config["platforms"]:
            if platform not in platforms:
                platforms[platform] = default["platforms"][platform]
                changed = True

    snapshot = {
        "version": 1,
        "created_at": existing.get(
            "created_at", datetime.now(TZ).isoformat()
        ),
        "updated_at": (
            datetime.now(TZ).isoformat()
            if changed
            else existing.get("updated_at", datetime.now(TZ).isoformat())
        ),
        "platforms": config["platforms"],
        "shop_aliases": config["shop_aliases"],
        "results": results,
    }
    write_json(path, snapshot)
    print(f"已初始化排名快照: {path}")
    return snapshot


def load_snapshot():
    """读取当天快照，不存在时自动初始化。"""
    path = current_snapshot_path()
    if not path.exists():
        return init_snapshot()
    return load_json(path)


def write_csv_template():
    """导出可人工填写或从平台结果复制的 CSV 模板。"""
    snapshot = load_snapshot()
    output_path = current_snapshot_path().with_suffix(".csv")
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "keyword_id",
                "query",
                "category",
                "platform",
                "mentioned",
                "matched_aliases",
                "position",
                "cited_source",
                "sentiment",
                "notes",
            ]
        )
        for keyword_id, item in snapshot["results"].items():
            for platform, result in item["platforms"].items():
                writer.writerow(
                    [
                        keyword_id,
                        item["query"],
                        item["category"],
                        platform,
                        "" if result["mentioned"] is None else int(result["mentioned"]),
                        "、".join(result["matched_aliases"]),
                        "" if result["position"] is None else result["position"],
                        result["cited_source"],
                        result["sentiment"],
                        result["notes"],
                    ]
                )
    print(f"已生成 CSV 模板: {output_path}")


def parse_bool(value):
    """解析 CSV 中的是/否值。"""
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "是", "提到", "命中"}:
        return True
    if normalized in {"0", "false", "no", "n", "否", "未提到", "未命中"}:
        return False
    if not normalized:
        return None
    raise ValueError(f"无法识别 mentioned 值: {value}")


def import_csv(csv_path):
    """导入人工填写的平台排名结果。"""
    snapshot = load_snapshot()
    imported = 0
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            keyword_id = row["keyword_id"].strip()
            platform = row["platform"].strip()
            item = snapshot["results"].get(keyword_id)
            if not item:
                raise ValueError(f"未知关键词编号: {keyword_id}")
            if platform not in item["platforms"]:
                raise ValueError(f"未知平台: {platform}")

            mentioned = parse_bool(row.get("mentioned", ""))
            aliases = [
                value.strip()
                for value in row.get("matched_aliases", "").replace(",", "、").split("、")
                if value.strip()
            ]
            position_text = row.get("position", "").strip()
            position = int(position_text) if position_text else None
            result = item["platforms"][platform]
            result.update(
                {
                    "status": "completed" if mentioned is not None else "pending",
                    "mentioned": mentioned,
                    "matched_aliases": aliases,
                    "position": position,
                    "cited_source": row.get("cited_source", "").strip(),
                    "sentiment": row.get("sentiment", "").strip(),
                    "notes": row.get("notes", "").strip(),
                }
            )
            imported += 1

    snapshot["updated_at"] = datetime.now(TZ).isoformat()
    write_json(current_snapshot_path(), snapshot)
    print(f"已导入 {imported} 条结果")
    return snapshot


def summarize():
    """统计平台、分类和整体提及率。"""
    snapshot = load_snapshot()
    overall = {"total": 0, "completed": 0, "mentioned": 0}
    by_platform = defaultdict(
        lambda: {"total": 0, "completed": 0, "mentioned": 0, "positions": []}
    )
    by_category = defaultdict(
        lambda: {"total": 0, "completed": 0, "mentioned": 0}
    )

    for item in snapshot["results"].values():
        for platform, result in item["platforms"].items():
            overall["total"] += 1
            by_platform[platform]["total"] += 1
            by_category[item["category"]]["total"] += 1
            if result["status"] != "completed":
                continue
            overall["completed"] += 1
            by_platform[platform]["completed"] += 1
            by_category[item["category"]]["completed"] += 1
            if result["mentioned"]:
                overall["mentioned"] += 1
                by_platform[platform]["mentioned"] += 1
                by_category[item["category"]]["mentioned"] += 1
                if result["position"]:
                    by_platform[platform]["positions"].append(result["position"])

    def rate(node):
        if not node["completed"]:
            return 0.0
        return node["mentioned"] / node["completed"] * 100

    summary = {
        "snapshot": str(current_snapshot_path()),
        "updated_at": snapshot["updated_at"],
        "overall": {**overall, "mention_rate": round(rate(overall), 1)},
        "by_platform": {},
        "by_category": {},
    }
    for platform, values in by_platform.items():
        average_position = (
            round(sum(values["positions"]) / len(values["positions"]), 1)
            if values["positions"]
            else None
        )
        summary["by_platform"][platform] = {
            **values,
            "mention_rate": round(rate(values), 1),
            "average_position": average_position,
        }
    for category, values in by_category.items():
        summary["by_category"][category] = {
            **values,
            "mention_rate": round(rate(values), 1),
        }

    latest_json = HISTORY_DIR / "latest.json"
    latest_md = HISTORY_DIR / "latest.md"
    write_json(latest_json, summary)
    lines = [
        "# AI 搜索可见性周报",
        "",
        f"- 快照文件：{current_snapshot_path().name}",
        f"- 更新时间：{summary['updated_at']}",
        f"- 已完成检查：{overall['completed']}/{overall['total']}",
        f"- 提及次数：{overall['mentioned']}",
        f"- 已检查命中率：{summary['overall']['mention_rate']}%",
        "",
        "## 平台表现",
        "",
        "| 平台 | 已完成 | 提及 | 命中率 | 平均位置 |",
        "|---|---:|---:|---:|---:|",
    ]
    for platform, values in summary["by_platform"].items():
        lines.append(
            f"| {platform} | {values['completed']}/{values['total']} | "
            f"{values['mentioned']} | {values['mention_rate']}% | "
            f"{values['average_position'] if values['average_position'] else '-'} |"
        )
    lines.extend(
        [
            "",
            "## 分类表现",
            "",
            "| 分类 | 已完成 | 提及 | 命中率 |",
            "|---|---:|---:|---:|",
        ]
    )
    for category, values in summary["by_category"].items():
        lines.append(
            f"| {category} | {values['completed']}/{values['total']} | "
            f"{values['mentioned']} | {values['mention_rate']}% |"
        )
    latest_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"已生成周报: {latest_md}")


def main():
    parser = argparse.ArgumentParser(description="AI 搜索排名监测")
    parser.add_argument("--init", action="store_true", help="初始化当天快照")
    parser.add_argument("--csv-template", action="store_true", help="导出 CSV 模板")
    parser.add_argument("--import-csv", help="导入已填写的 CSV")
    parser.add_argument("--summary", action="store_true", help="生成最新汇总")
    args = parser.parse_args()

    if args.csv_template:
        write_csv_template()
    elif args.import_csv:
        import_csv(args.import_csv)
        summarize()
    elif args.summary:
        summarize()
    else:
        init_snapshot()
        summarize()


if __name__ == "__main__":
    main()
