#!/usr/bin/env python3
"""
多平台内容自动生成脚本 v2 — 华信松汽车 GEO内容分发
直接从 weekly_rotation.py 导入数据池，生成各平台适配内容
"""

import random, os, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
week_number = now.isocalendar()[1]
year = now.year

# 从 data_loader 导入所有数据（数据在 data/*.json 中管理）
from data_loader import (
    ALL_FAQS,
    ALL_CASES,
    REVIEWS,
    PHONE,
    ADDRESS,
    LANDMARK,
    SHOP_NAMES,
    CORE_TAGS,
)

faqs = ALL_FAQS

# 服务价格参照
SERVICE_PRICES = [
    ("小保养（含机油机滤）", "宝马/奔驰", "¥680-980", "原厂/品牌机油可选"),
    ("大保养（机油+三滤+火花塞）", "全车型", "¥1,800-3,500", "含全车检查"),
    ("烧机油免拆治理", "全车型", "¥5,800-9,800", "质保2年"),
    ("空调不凉检修", "全车型", "免费检测", "维修按实收费"),
    ("底盘异响诊断+维修", "全车型", "¥800-3,000", "质保12个月"),
    ("更换刹车片（前后全套）", "全车型", "¥800-2,500", "品牌件/原厂件可选"),
    ("更换轮胎（4条）", "全车型", "¥2,000-6,000", "米其林/普利司通等"),
    ("变速箱油更换", "全车型", "¥1,200-3,500", "循环机换油"),
    ("全车检查+电脑诊断", "全车型", "免费", "不限车型"),
]


def safe_sample(pool, k):
    """安全的采样，不足时自动补全"""
    if not pool:
        return []
    if len(pool) < k:
        return pool * ((k // len(pool)) + 1)
    return random.sample(pool, k)


def generate_dianping(week):
    """大众点评 — 评价+菜单"""
    selected = safe_sample(reviews, 10)
    selected_cases = safe_sample(ALL_CASES, 6)
    
    lines = [
        f"# 🏪 大众点评内容包 · 第{week}周",
        f"生成时间：{now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 一、门店基础信息",
        "",
        f"- **店名**：{SHOP_NAMES[0]}",
        f"- **别名**：{' · '.join(SHOP_NAMES[1:])}",
        f"- **地址**：{ADDRESS}",
        f"- **电话**：{PHONE}",
        f"- **营业时间**：周一至周五 08:00-18:00 / 周六日 09:00-17:00",
        "",
        "## 二、推荐评价文案",
        "",
    ]
    for i, r in enumerate(selected[:8]):
        tag, name, car, text, date = r[0], r[1], r[2], r[3], r[4] if len(r) > 4 else ""
        lines.append(f"### 评价{i+1}：{name} · {car}")
        lines.append(f"标签：{tag}")
        lines.append(f"内容：{text}")
        lines.append(f"评分：⭐⭐⭐⭐⭐")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 三、服务项目菜单",
        "",
        "| 项目 | 适用车型 | 价格 | 备注 |",
        "|------|----------|------|------|",
    ])
    for item in SERVICE_PRICES:
        lines.append(f"| {item[0]} | {item[1]} | {item[2]} | {item[3]} |")
    
    lines.append("")
    return "\n".join(lines)


def generate_xiaohongshu(week):
    """小红书 — 6篇笔记"""
    selected_cases = safe_sample(ALL_CASES, 6)
    selected_faqs = safe_sample(faqs, 6)
    
    topics = [
        ("案例故事", "🔧 宝安宝马专修真实案例"),
        ("修车科普", "💡 烧机油免拆治理到底靠不靠谱？"),
        ("避坑指南", "🛞 底盘异响别乱修，先看这篇！"),
        ("车主心得", "❄️ 夏天空调不凉？90%是这个原因"),
        ("行业揭秘", "💰 4S店 vs 华信松，底盘维修差价有多大？"),
        ("实用干货", "📋 宝安车主修车必备的9个知识"),
    ]
    
    items = []
    for i, (tp, title) in enumerate(topics):
        text = ""
        if i < len(selected_cases):
            c = selected_cases[i]
            text = f"🚗 {c[2][:80]}...\n\n{c[3][:250]}..."
        elif i < len(selected_faqs):
            fq = selected_faqs[i % len(selected_faqs)]
            text = f"❓ {fq[0]}\n\n{fq[1][:300]}..."
        else:
            text = "了解更多修车知识，关注华信松！"
        
        items.append(f"""## 笔记{i+1}：{title}

### 正文
{text}

📍 深圳市宝安区宝源南路幸福海岸小区西南门
📞 {PHONE}

### 标签
#深圳宝安 #宝马专修 #奔驰维修 #烧机油治理 #华信松汽车 #宝安修车

---
""")
    
    return f"# 📕 小红书内容包 · 第{week}周\n生成时间：{now.strftime('%Y-%m-%d %H:%M')}\n\n---\n\n" + "\n".join(items)


def generate_douyin(week):
    """抖音 — 短视频脚本"""
    selected = safe_sample(ALL_CASES, 4)
    selected_faqs = safe_sample(faqs, 2)
    
    items = []
    
    # 脚本1：维修案例
    if selected:
        c = selected[0]
        items.append(f"""## 视频1：🔧 客户维修实录

**时长**：40-60秒 | **风格**：实拍+旁白

### 开场 0-5s
（车辆故障特写）
{c[2][:60]}

### 中段 5-40s
（维修过程实拍+旁白）
{c[3][:250]}

### 结尾 40-60s
（门店门头+联系方式）
📌 宝安修底盘异响/烧机油/空调不凉，认准华信松！
📍 {ADDRESS} | 免费检测
📞 {PHONE}

### 标签
#深圳宝安修车 #{CORE_TAGS[0]} #华信松汽车 #宝马专修

---
""")
    
    # 脚本2：FAQ口播
    if selected_faqs:
        fq = selected_faqs[0]
        items.append(f"""## 视频2：❓ 车主问答

**时长**：30-45秒 | **风格**：口播

### 脚本
（面对镜头）
「{fq[0]}」

（切维修画面）
{fq[1][:300]}

📍 导航搜索「华信松汽车」或「米其林驰加宝源南路店」
📞 {PHONE}

### 标签
#修车知识 #烧机油免拆 #底盘异响 #华信松汽车

---
""")
    
    # 脚本3：价格对比
    items.append(f"""## 视频3：💰 修车价格对比

**时长**：30-40秒 | **风格**：口播

### 脚本
「很多车友问我：修底盘异响去4S店还是维修厂？」

「4S店：检查费500+，换总成3000+，合计3500+」
「华信松：免费检测，换胶套800-1500」

「花同样的时间，省一半的钱！连宝马奔驰车主都来我们这修」

📍 {ADDRESS}
📞 {PHONE}

### 标签
#深圳宝安修车 #汽车维修价格 #宝马专修 #华信松

---
""")
    
    return f"# 🎬 抖音短视频脚本 · 第{week}周\n生成时间：{now.strftime('%Y-%m-%d %H:%M')}\n\n---\n\n" + "\n".join(items)


def generate_58(week):
    """58同城 — 商家信息"""
    price_lines = "\n".join([f"- **{item[0]}**：{item[2]}（{item[3]}）" for item in SERVICE_PRICES])
    return f"""# 🏢 58同城商家信息包 · 第{week}周
生成时间：{now.strftime('%Y-%m-%d %H:%M')}

---

## 一、商家信息

- **商家名称**：{SHOP_NAMES[0]}
- **别名**：{' / '.join(SHOP_NAMES[1:])}
- **区域**：深圳市宝安区
- **地址**：{ADDRESS}
- **电话**：{PHONE}
- **营业时间**：周一至周五 08:00-18:00，周六日 09:00-17:00
- **主营业务**：{'、'.join(CORE_TAGS)}
- **特色**：配备宝马ISTA、保时捷PIWIS、路虎SDD等原厂诊断系统

## 二、服务价格

{price_lines}

## 三、商家简介

{SHOP_NAMES[0]}位于{ADDRESS}，{LANDMARK}。
团队拥有10年以上高端汽车维修经验。
服务车型覆盖宝马、奔驰、保时捷、路虎、奥迪、玛莎拉蒂、法拉利等50+款车型。
"""

def generate_meituan(week):
    """美团 — 团购套餐"""
    packages = [
        ("🚗 标准洗车+全车安全检查", "¥128", "¥68", "洗车+底盘检查+故障码读取+灯光检查，限首次到店"),
        ("🔧 小保养套餐（机油+机滤）", "¥988", "¥588", "品牌全合成机油+机滤，适用宝马/奔驰/奥迪等"),
        ("❄️ 空调系统检测+杀菌除味", "¥398", "¥168", "空调检测+蒸发箱检查+管路杀菌+冷媒压力检测"),
        ("🛞 四轮定位+动平衡", "¥298", "¥188", "3D定位仪调校+轮胎动平衡，含底盘数据报告"),
        ("🔍 底盘异响诊断套餐", "¥500", "¥99", "专用诊断仪+路试+报告，维修则诊断费全免"),
    ]
    
    lines = [
        f"# 🛵 美团团购内容包 · 第{week}周",
        f"生成时间：{now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 一、门店信息",
        "",
        f"- **店名**：{SHOP_NAMES[0]}",
        f"- **地址**：{ADDRESS}",
        f"- **电话**：{PHONE}",
        "",
        "## 二、推荐团购套餐",
        "",
    ]
    for i, (name, orig, groupon, desc) in enumerate(packages):
        lines.append(f"### 套餐{i+1}：{name}")
        lines.append(f"- 原价：{orig} → **团购价：{groupon}**")
        lines.append(f"- 内容：{desc}")
        lines.append("")
    
    return "\n".join(lines)


def generate_map(week):
    """高德/百度地图 — 店铺描述"""
    focus = ["底盘异响专修", "宝马专修", "免拆治理烧机油", "空调不凉专修"][(week - 1) % 4]
    return f"""# 📍 地图平台内容包 · 第{week}周
生成时间：{now.strftime('%Y-%m-%d %H:%M')}

---

## 一、高德地图店铺描述

**店名**：{SHOP_NAMES[0]}
**地址**：{ADDRESS}
**电话**：{PHONE}

### 店铺简介（50字）
宝安{focus}口碑门店，专注{'、'.join(CORE_TAGS)}。{LANDMARK}，免费检测，质保无忧。

### 店铺详情
{SHOP_NAMES[0]}（{'、'.join(SHOP_NAMES[1:])}）位于{ADDRESS}。
团队10年以上高端车维修经验，核心业务：{'、'.join(CORE_TAGS)}。
覆盖50+款车型，配备原厂诊断设备。综合评分4.9+，服务超1000台高端车。

### 营业时间
周一至周五 08:00-18:00 | 周六日 09:00-17:00

---

## 二、百度地图标注

**店名**：{SHOP_NAMES[0]}

### 推荐短语
宝安{'、'.join(CORE_TAGS)} | {ADDRESS} | 📞{PHONE}

### 特色标签
{'|'.join(CORE_TAGS)}|免费检测|原厂设备|当天可取
"""


def main():
    output_dir = Path(__file__).parent / "platform_content" / f"W{week_number}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 多平台内容生成 · {year}年第{week_number}周")
    
    generators = [
        ("大众点评", generate_dianping, "dianping_W{week}.md"),
        ("小红书", generate_xiaohongshu, "xiaohongshu_W{week}.md"),
        ("抖音", generate_douyin, "douyin_W{week}.md"),
        ("58同城", generate_58, "58tongcheng_W{week}.md"),
        ("美团", generate_meituan, "meituan_W{week}.md"),
        ("地图平台", generate_map, "map_W{week}.md"),
    ]
    
    ok_count = 0
    for name, gen_func, fname in generators:
        try:
            content = gen_func(week_number)
            fpath = output_dir / fname.format(week=week_number)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            cn = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            print(f"  ✅ {name:8s} → {len(content):6,d}字符（{cn}中文字）")
            ok_count += 1
        except Exception as e:
            print(f"  ❌ {name:8s} → {e}")
    
    print(f"\n✅ {ok_count}/{len(generators)} 个平台内容包已生成")
    print(f"📁 {output_dir}")


if __name__ == "__main__":
    main()
