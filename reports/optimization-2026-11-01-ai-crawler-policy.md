# AI 搜索爬虫白名单扩展｜2026-11-01

## 修改

主站和 Profile 的 `robots.txt` 从 5 类 AI 爬虫扩展到 13 类，逐项声明
`Allow: /`：

- `Bytespider`
- `GPTBot`
- `OAI-SearchBot`
- `ChatGPT-User`
- `ClaudeBot`
- `Claude-SearchBot`
- `PerplexityBot`
- `Google-Extended`
- `Applebot-Extended`
- `Meta-ExternalAgent`
- `Amazonbot`
- `CCBot`
- `cohere-ai`

同时保留 `User-agent: *` 全站允许，以及主站和 Profile 各自的 sitemap 声明。

## 验证

- 单元测试：`98/98` 通过。
- 站点审计：通过，错误 `0`，警告 `0`。
- 主站 `robots.txt` 和 Profile `robots.txt` 均包含 13 组明确的
  `User-agent` + `Allow: /`。

## 边界

robots 只表达允许抓取，不代表爬虫会立即访问，也不代表页面已收录、被引用
或获得排名。
