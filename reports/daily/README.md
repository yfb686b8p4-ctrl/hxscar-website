# 每日搜索检查目录

每天执行：

```bash
python3 scripts/daily_control.py --prepare
```

该命令会生成：

- `YYYY-MM-DD-plan.json`：当天护栏问题和轮换问题。
- `YYYY-MM-DD-results.csv`：待填写结果。
- `status_snapshot`：Git、LaunchAgent、线上页面和发布平台状态。

完成豆包、元宝实测后填写 CSV，再执行：

```bash
python3 scripts/daily_control.py --finalize reports/daily/YYYY-MM-DD-results.csv
```

系统会生成日报、与上一份日报的差异、异常优先待办和 `latest.md`。
