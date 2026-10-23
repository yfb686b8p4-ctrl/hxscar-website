#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成本地权威平台发布队列并跟踪状态。"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "external_platforms.json"
PUBLISHING_DIR = ROOT / "publishing"
STATUS_PATH = PUBLISHING_DIR / "status.json"
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


def load_status():
    """读取平台状态，不存在时返回空状态。"""
    if STATUS_PATH.exists():
        return load_json(STATUS_PATH)
    return {"updated_at": "", "platforms": {}}


def queue_week(week):
    """生成指定周的发布队列。"""
    config = load_json(CONFIG_PATH)
    status = load_status()
    if not STATUS_PATH.exists():
        write_json(STATUS_PATH, status)
    queue_dir = PUBLISHING_DIR / "queue" / f"W{week}"
    queue_dir.mkdir(parents=True, exist_ok=True)
    shop = config["shop"]
    tasks = []

    for platform in config["platforms"]:
        platform_id = platform["id"]
        source = ROOT / "platform_content" / f"W{week}" / platform[
            "content_source"
        ].format(week=week)
        source_text = (
            source.read_text(encoding="utf-8")
            if source.exists()
            else f"未找到本周内容源：{source.relative_to(ROOT)}"
        )
        stored = status["platforms"].get(platform_id, {})
        current_status = stored.get("status", "pending")
        task_path = queue_dir / f"{platform['priority'].lower()}-{platform_id}.md"
        task_text = f"""# {platform['name']}发布任务

- 平台优先级：{platform['priority']}
- 当前状态：{current_status}
- 目标：{platform['objective']}
- 操作入口：{platform['action_url']}
- 内容来源：`{source.relative_to(ROOT) if source.exists() else source}`

## 必须统一的门店信息

- 全称：{shop['canonical_name']}
- 工商登记名称：{shop.get('registered_name', '')}
- 别名：{'、'.join(shop['aliases'])}
- 电话：{shop['phone']}
- 座机：{shop.get('landline', '')}
- 地址：{shop['address']}
- 导航地址：{shop.get('navigation_address', '')}
- 营业时间：{shop['hours']}

{shop.get('entity_scope_statement', '')}

{shop.get('identity_statement', '')}

## 发布内容

{source_text}

## 完成检查

- [ ] 名称、地址、电话与上方信息一致
- [ ] 主营项目包含宝马专修、豪车保养、空调、底盘和老车整备
- [ ] 已补充真实门店或施工图片
- [ ] 已保存发布链接和截图
- [ ] 已运行 `python3 scripts/authority_queue.py --mark {platform_id} --status published --url <链接>`
"""
        task_path.write_text(task_text, encoding="utf-8")
        tasks.append(
            {
                "id": platform_id,
                "name": platform["name"],
                "priority": platform["priority"],
                "status": current_status,
                "objective": platform["objective"],
                "action_url": platform["action_url"],
                "task_file": str(task_path.relative_to(ROOT)),
                "source_file": str(source.relative_to(ROOT))
                if source.exists()
                else "",
                "url": stored.get("url", ""),
                "notes": stored.get("notes", ""),
            }
        )

    manifest = {
        "week": f"W{week}",
        "generated_at": datetime.now(TZ).date().isoformat(),
        "shop": shop,
        "tasks": tasks,
    }
    write_json(queue_dir / "manifest.json", manifest)
    write_report(tasks)
    print(f"已生成 W{week} 发布队列: {queue_dir}")
    print(f"任务数量: {len(tasks)}")
    return manifest


def write_report(tasks=None):
    """生成所有平台的状态看板。"""
    if tasks is None:
        status = load_status()
        config = load_json(CONFIG_PATH)
        tasks = []
        for platform in config["platforms"]:
            stored = status["platforms"].get(platform["id"], {})
            tasks.append(
                {
                    "id": platform["id"],
                    "name": platform["name"],
                    "priority": platform["priority"],
                    "status": stored.get("status", "pending"),
                    "objective": platform["objective"],
                    "action_url": platform["action_url"],
                    "url": stored.get("url", ""),
                    "notes": stored.get("notes", ""),
                }
            )

    lines = [
        "# 站外权威平台执行看板",
        "",
        f"更新时间：{datetime.now(TZ).date().isoformat()}",
        "",
        "| 优先级 | 平台 | 状态 | 目标 | 发布链接 | 备注 |",
        "|---|---|---|---|---|---|",
    ]
    for task in tasks:
        link = task.get("url") or "-"
        lines.append(
            f"| {task['priority']} | {task['name']} | {task['status']} | "
            f"{task['objective']} | {link} | {task.get('notes') or '-'} |"
        )
    lines.extend(
        [
            "",
            "## 使用方式",
            "",
            "1. 打开每周 `publishing/queue/Wxx` 目录。",
            "2. 按 P0、P1、P2 顺序完成平台发布。",
            "3. 发布后用 `--mark` 记录真实 URL 和备注。",
            "4. 每周查看本看板，未发布任务不会自动算作完成。",
        ]
    )
    PUBLISHING_DIR.mkdir(parents=True, exist_ok=True)
    (PUBLISHING_DIR / "STATUS.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def mark_platform(platform_id, state, url, notes):
    """更新单个平台发布状态。"""
    config = load_json(CONFIG_PATH)
    valid_ids = {platform["id"] for platform in config["platforms"]}
    if platform_id not in valid_ids:
        raise ValueError(f"未知平台: {platform_id}")
    if state not in {"pending", "published", "blocked", "review"}:
        raise ValueError(f"未知状态: {state}")

    status = load_status()
    status["platforms"][platform_id] = {
        "status": state,
        "url": url or "",
        "notes": notes or "",
        "updated_at": datetime.now(TZ).isoformat(),
    }
    status["updated_at"] = datetime.now(TZ).isoformat()
    write_json(STATUS_PATH, status)
    write_report()
    print(f"已更新 {platform_id}: {state}")


def main():
    parser = argparse.ArgumentParser(description="站外权威平台发布队列")
    parser.add_argument("--week", help="ISO 周数，例如 43")
    parser.add_argument("--report", action="store_true", help="只生成状态看板")
    parser.add_argument("--mark", help="更新平台 ID")
    parser.add_argument(
        "--status",
        choices=["pending", "published", "blocked", "review"],
        default="published",
    )
    parser.add_argument("--url", default="", help="真实发布链接")
    parser.add_argument("--notes", default="", help="发布备注")
    args = parser.parse_args()

    if args.mark:
        mark_platform(args.mark, args.status, args.url, args.notes)
        return
    if args.report:
        write_report()
        print(f"已生成看板: {PUBLISHING_DIR / 'STATUS.md'}")
        return

    week = args.week or datetime.now(TZ).strftime("%V")
    queue_week(week)


if __name__ == "__main__":
    main()
