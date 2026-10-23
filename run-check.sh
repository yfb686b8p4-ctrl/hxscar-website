#!/bin/bash
# 每日AI搜索检查一键脚本
# 使用: bash run-check.sh

cd "$(dirname "$0")"
echo "🔍 开始每日AI搜索检查..."
echo "   门店: 华信松汽车服务（幸福海岸分公司）"
echo "   时间: $(date '+%Y-%m-%d %H:%M')"
echo ""

python3 scripts/daily_control.py --prepare

echo ""
echo "✅ 今日检测计划和系统状态已生成"
echo "📝 填写当日 results.csv 后运行："
echo "python3 scripts/daily_control.py --finalize reports/daily/YYYY-MM-DD-results.csv"
