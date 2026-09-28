# 华信松汽车 AI 搜索内容站

本项目为深圳宝安华信松汽车服务有限公司维护静态内容站和每周 GEO（生成式搜索优化）内容。

线上地址：

- 首页：<https://yfb686b8p4-web.github.io/hxscar-website/>
- 完整 FAQ：<https://yfb686b8p4-web.github.io/hxscar-website/faq.html>
- 维修案例：<https://yfb686b8p4-web.github.io/hxscar-website/cases.html>
- 资料索引：<https://yfb686b8p4-web.github.io/hxscar-website/llms.txt>

## 当前内容规模

| 内容 | 数量 |
|---|---:|
| FAQ | 127 |
| 维修案例 | 56 |
| 评价摘录 | 30 |
| 覆盖车型 | 54 |
| 平台内容包 | 每周 6 个 |

## 每周自动流程

GitHub Actions 每周一北京时间 08:00 执行：

1. 更新首页和四周关键词轮换配置。
2. 生成大众点评、小红书、抖音、58 同城、美团和地图平台内容包。
3. 生成完整 FAQ 页、案例页、`robots.txt`、`sitemap.xml` 和 `llms.txt`。
4. 执行站点质量审计并保存报告。
5. 保存当周平台内容包。
6. 提交更新并部署 GitHub Pages。

## 本地执行

```bash
python3 weekly_rotation.py
python3 scripts/site_builder.py
python3 multi_platform_publisher.py
python3 scripts/site_audit.py
```

审计结果：

- `reports/site-audit.json`
- `reports/site-audit.md`

## 目录说明

| 目录 | 用途 |
|---|---|
| `data/` | FAQ、案例、评价、门店资料和关键词配置 |
| `scripts/` | 静态页生成和站点质量审计 |
| `platform_content/` | 每周多平台内容包 |
| `reports/` | 审计及排名检测结果 |
| `.github/workflows/` | 每周自动更新和部署流程 |

## 真实性原则

- 不再自动生成随机评分或评价数量。
- 页面不把未核验内容标记为“真实案例”或“真实评价”。
- 医疗、费用、维修结论均以门店到店检测为准。
- 外部平台账号和地图 API 密钥不得写入仓库。
