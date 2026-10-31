# AI 证据数量一致性修复｜2026-11-01

## 问题

标准答案已从 15 条增加到 16 条，但两处公开机器入口仍保留旧计数：

- 主站 `llms.txt` 将 GitHub Gist 镜像写成“15 条逐行问答”；
- Profile Pages 的 `llms.txt` 和 `answers.html` 写成“15 条原子问答证据”。

这会让 AI 读取到与 `qa-evidence.jsonl`、Release 和 Gist 实际 16 行不一致的
规模信息。

## 修复

- 主站 `llms.txt` 改为从 `len(SEARCH_ANSWERS)` 动态生成当前答案数。
- Profile `llms.txt` 改为 16 条。
- Profile `answers.html` 的下载入口改为 16 条。
- 新增回归测试，要求机器语料包含当前答案数且不再出现“15 条逐行问答”。

## 验证

- 当前标准答案：16 条。
- 单元测试：`104/104` 通过。
- 站点审计：通过，错误 `0`。
- 主站与 Profile 文本入口均已检出 16 条。

## 边界

该修复只保证公开机器语料的数量口径一致，不代表平台已收录、引用或排名。
