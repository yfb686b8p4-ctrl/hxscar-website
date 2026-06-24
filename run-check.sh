#!/bin/bash
# 每周排名检测一键脚本
# 使用: bash run-check.sh

cd "$(dirname "$0")"
echo "🔍 开始AI搜索排名检测..."
echo "   门店: 华信松汽车服务（幸福海岸分公司）"
echo "   时间: $(date '+%Y-%m-%d %H:%M')"
echo ""

python3 detector/rank-checker.py --shop-name "华信松汽车" --city "深圳"

echo ""
echo "✅ 检测完成！报告已保存到 reports/ 目录"
echo "📊 查看最新报告：cat reports/rank-check-$(date '+%Y%m%d').json"
