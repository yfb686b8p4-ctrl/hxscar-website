# jsDelivr 外部证据镜像与实体复测｜2026-11-01

## 动机

元宝全新会话仍判断
`深圳市华信松汽车服务有限公司幸福海岸分公司`与“老周修车”不是同一家，
并继续引用腾讯地图旧号码 `13923454895`。豆包全新会话能确认同一家，
但只返回地址的一部分，没有当前双电话和营业时间。

两个平台均未读取本轮更新的官网页面，因此本轮增加无需登录即可公开访问的
独立 CDN 镜像，并把它纳入网站实体图和自动化一致性检查。

## 已发布镜像

- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@ai-evidence-cdn-2026-11-01/store-facts.json`
- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@ai-evidence-cdn-2026-11-01/store-facts.jsonld`
- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@ai-evidence-cdn-2026-11-01/entity-corrections.json`
- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@ai-evidence-cdn-2026-11-01/qa-evidence.jsonl`

## 发布前交叉核验

- 四个地址均返回 HTTP 200。
- `store-facts.json` SHA-256：
  `d925307e56be4300e73a043f10fa04e45862e6f618f94b3aadc3940983fcdd89`
- `store-facts.jsonld` SHA-256：
  `5457df8896b02b7819d6cd0d37a2d1e063c9275791c9783acd798d2880ff83d7`
- `entity-corrections.json` SHA-256：
  `24729570d529a84b4f0247b799bf4572b22485fb90474457a913bd18e3981515`
- `qa-evidence.jsonl` SHA-256：
  `e052e3d8bdef60e82e88db840b131f9e2a20aa3731fd2685ac83ceae433fe983`
- 上述 CDN 文件与本地文件 SHA-256 逐一一致。
- CDN 响应通过 Cloudflare 提供，支持 HTTPS 和跨域读取。
- 使用不可变 Git 标签 `ai-evidence-cdn-2026-11-01`，避免 `@main`
  缓存漂移和自引用循环。

## 官网接入

- 门店 `AutoRepair.subjectOf` 增加四个 jsDelivr `DataFeed`。
- `store-facts.json` 的 `citationTargets` 增加四个 CDN 证据入口。
- `entity-corrections.json` 增加 CDN 纠错镜像。
- 标准答案证据列表增加四个 CDN 镜像。
- 一致性检查器新增 jsDelivr 的问答、门店事实、JSON-LD 和纠错文件检查。
- 每日在线检查从 41 项扩展到 45 项。

## 验证结果

- 单元测试：`94/94` 通过。
- 站点审计：通过，错误 `0`，警告 `0`。
- 所有生成文件 JSON/JSON-LD 解析通过。

## 复测边界

复测只能证明平台在特定全新会话中的当前回答。jsDelivr 镜像的发布和官网引用
不代表 jsDelivr、元宝或豆包已经收录、引用或改变排名。
