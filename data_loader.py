#!/usr/bin/env python3
"""
数据加载器 — 从 data/ 目录加载所有数据
供 weekly_rotation.py 和 multi_platform_publisher.py 等模块调用
"""

import json
from pathlib import Path

_data_dir = Path(__file__).parent / "data"


def _load_json(filename):
    """加载 JSON 数据文件"""
    path = _data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"数据文件未找到: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ====== 门店基本信息 ======
_shop = _load_json("shop_info.json")
PHONE = _shop["phone"]
ADDRESS = _shop["address"]
LANDMARK = _shop["landmark"]
SHOP_NAMES = _shop["shop_names"]
CORE_TAGS = _shop["core_tags"]
COVERED_MODELS = _shop["covered_models"]

# ====== FAQ 数据 ======
# 保持与旧版相同的格式（列表套元组），兼容旧代码
_raw_faqs = _load_json("faqs.json")
ALL_FAQS = [(item["question"], item["answer"]) for item in _raw_faqs]

# ====== 维修案例 ======
_raw_cases = _load_json("cases.json")
_f_fields = ["tag", "car_type", "issue", "solution", "price", "result", "source"]
ALL_CASES = []
for item in _raw_cases:
    if isinstance(item, dict):
        ALL_CASES.append(tuple(item.get(f, "") for f in _f_fields))
    else:
        ALL_CASES.append(item)

# ====== 车主评价 ======
_raw_reviews = _load_json("reviews.json")
_r_fields = ["tag", "name", "car_model", "content", "date"]
REVIEWS = []
for item in _raw_reviews:
    if isinstance(item, dict):
        REVIEWS.append(tuple(item.get(f, "") for f in _r_fields))
    else:
        REVIEWS.append(item)

# ====== 每周关键词轮换配置 ======
WEEKLY_CONFIGS = _load_json("weekly_configs.json")
