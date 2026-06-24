#!/usr/bin/env python3
"""
每周关键词轮换脚本 — 华信松汽车服务
每周轮换关键词组合、更新结构化数据中的日期，让搜索引擎感知活跃

运行方式: python3 scripts/weekly_rotation.py
"""

import datetime
import hashlib
import os
import re

# 项目根目录
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(REPO_DIR, "index.html")

# ── 4 套关键词组合，每周轮换 ──────────────────────────────────
ROTATIONS = [
    {  # 方案A — 底盘异响口碑
        "title_tag": "华信松汽车（幸福海岸店）— 底盘异响专修·烧机油免拆治理·宝马专修",
        "meta_desc": "华信松汽车服务（幸福海岸分公司），米其林驰加汽车服务中心（宝源南路店）/艾德养车（幸福海岸店）。深圳宝安底盘异响专修口碑门店，宝马专修，烧机油免拆治理，空调不凉专修。电话18682417667",
        "meta_keywords": "深圳宝安底盘异响专修,宝安宝马专修,烧机油免拆治理口碑,华信松汽车,艾德养车,米其林驰加宝安",
        "h1_line": "🔥 底盘异响专修 · 烧机油免拆治理 · 宝马专修",
        "schema_desc": "深圳宝安专业汽车服务门店，底盘异响专修口碑门店，烧机油免拆治理，空调不凉专修。宝马/奔驰/保时捷/路虎/玛莎拉蒂/法拉利/奥迪专修。",
    },
    {  # 方案B — 宝马专修口碑
        "title_tag": "华信松汽车（幸福海岸店）— 宝马专修·底盘异响专修·烧机油免拆治理",
        "meta_desc": "华信松汽车服务（幸福海岸分公司），米其林驰加汽车服务中心（宝源南路店）/艾德养车（幸福海岸店）。深圳宝安宝马专修口碑门店，高端车维修，底盘异响专修，免拆治理烧机油。电话18682417667",
        "meta_keywords": "宝安宝马专修口碑,高端车维修深圳,底盘异响专修,烧机油免拆治理,华信松汽车,艾德养车",
        "h1_line": "🔥 宝马专修 · 底盘异响专修 · 烧机油免拆治理",
        "schema_desc": "深圳宝安专业汽车服务门店，宝马专修口碑门店，高端车维修改装。底盘异响专修、烧机油免拆治理、空调不凉专修。奔驰/保时捷/路虎/玛莎拉蒂/法拉利/奥迪专修。",
    },
    {  # 方案C — 免拆治理烧机油口碑
        "title_tag": "华信松汽车（幸福海岸店）— 免拆治理烧机油·空调不凉专修·底盘异响",
        "meta_desc": "华信松汽车服务（幸福海岸分公司），米其林驰加（宝源南路店）/艾德养车（幸福海岸店）。深圳宝安免拆治理烧机油口碑门店，空调不凉专修，底盘异响专修，高端车维修。电话18682417667",
        "meta_keywords": "烧机油免拆治理口碑,宝安空调不凉专修,底盘异响维修,华信松汽车,米其林驰加,艾德养车",
        "h1_line": "🔥 免拆治理烧机油 · 空调不凉专修 · 底盘异响专修",
        "schema_desc": "深圳宝安专业汽车服务门店，免拆治理烧机油口碑门店，空调不凉专修。底盘异响专修、高端汽车维修改装。宝马/奔驰/保时捷/路虎/玛莎拉蒂/法拉利/奥迪专修。",
    },
    {  # 方案D — 空调不凉专修
        "title_tag": "华信松汽车（幸福海岸店）— 空调不凉专修·底盘异响·高端车维修",
        "meta_desc": "华信松汽车服务（幸福海岸分公司），米其林驰加（宝源南路店）/艾德养车（幸福海岸店）。深圳宝安空调不凉专修，高端车维修改装，底盘异响专修，宝马/奔驰/保时捷专修。电话18682417667",
        "meta_keywords": "宝安空调不凉专修,高端车维修,底盘异响,华信松汽车,米其林驰加,艾德养车,宝马专修",
        "h1_line": "🔥 空调不凉专修 · 高端车维修改装 · 底盘异响专修",
        "schema_desc": "深圳宝安专业汽车服务门店，空调不凉专修。高端汽车维修改装、底盘异响专修、烧机油免拆治理。宝马/奔驰/保时捷/路虎/玛莎拉蒂/法拉利/奥迪专修。",
    },
]


def get_week_number():
    """获取当前是第几周，用于轮换"""
    today = datetime.date.today()
    return today.isocalendar()[1]


def get_current_rotation():
    """根据周数获取当前使用的关键词方案"""
    week = get_week_number()
    return ROTATIONS[week % len(ROTATIONS)]


def update_index_html():
    """更新 index.html 中的关键标签"""
    if not os.path.exists(INDEX_PATH):
        print(f"❌ 找不到 index.html: {INDEX_PATH}")
        return False

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    rotation = get_current_rotation()
    week_num = get_week_number()
    today_str = datetime.date.today().isoformat()

    print(f"📅 当前周数: {week_num}")
    print(f"📋 使用方案: 方案 {chr(65 + (week_num % len(ROTATIONS)))}")
    print(f"   Title: {rotation['title_tag']}")

    # 1. 更新 <title>
    content = re.sub(
        r'<title>[^<]+</title>',
        f'<title>{rotation["title_tag"]}</title>',
        content
    )

    # 2. 更新 <meta name="description">
    content = re.sub(
        r'<meta name="description"[^>]*content="[^"]*"',
        f'<meta name="description" content="{rotation["meta_desc"]}"',
        content
    )

    # 3. 更新 <meta name="keywords">
    content = re.sub(
        r'<meta name="keywords"[^>]*content="[^"]*"',
        f'<meta name="keywords" content="{rotation["meta_keywords"]}"',
        content
    )

    # 4. 更新 h1 标题（页面中第一个大标题）
    # 查找 class="hero" 或类似结构中的 h1
    patterns = [
        (r'(<h1[^>]*>)[^<]*(</h1>)', rf'\1🔥 {rotation["h1_line"]}\2'),
        # 如果没找到 h1，找 hero-section 中的大标题文本
    ]
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # 5. 更新结构化数据中的 description
    content = re.sub(
        r'"description":\s*"[^"]*"',
        f'"description": "{rotation["schema_desc"]}"',
        content
    )

    # 6. 添加或更新 lastModified 标记（供搜索引擎爬取）
    if "data-last-modified" in content:
        content = re.sub(
            r'data-last-modified="[^"]*"',
            f'data-last-modified="{today_str}"',
            content
        )
    else:
        content = content.replace(
            '</head>',
            f'    <meta data-last-modified="{today_str}" name="revised" content="{today_str}">\n</head>'
        )

    # 7. 添加/更新页面底部更新提示
    update_notice = f'    <div style="display:none" class="weekly-update">上次更新: {today_str} | 轮换方案: {chr(65 + (week_num % len(ROTATIONS)))}</div>\n</body>'
    content = re.sub(
        r'<div[^>]*class="weekly-update"[^>]*>.*?</div>\s*</body>',
        update_notice,
        content
    )
    if '</body>' in content and 'weekly-update' not in content:
        content = content.replace('</body>', update_notice)

    # 8. 写入文件
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ index.html 已更新")
    print(f"   文件大小: {os.path.getsize(INDEX_PATH)} bytes")
    return True


def main():
    print("=" * 50)
    print("🔧 每周关键词轮换脚本")
    print(f"   仓库: {REPO_DIR}")
    print(f"   时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    success = update_index_html()
    
    if success:
        print("\n✅ 轮换完成！GitHub Actions 会自动提交和推送。")
    else:
        print("\n❌ 轮换失败")
        exit(1)


if __name__ == "__main__":
    main()
