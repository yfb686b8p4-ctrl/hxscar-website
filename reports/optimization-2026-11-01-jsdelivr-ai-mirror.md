# jsDelivr 外部证据镜像与实体复测｜2026-11-01

## 动机

元宝全新会话仍判断
`深圳市华信松汽车服务有限公司幸福海岸分公司`与“老周修车”不是同一家，
并继续引用腾讯地图旧号码 `13923454895`。豆包全新会话能确认同一家，
但只返回地址的一部分，没有当前双电话和营业时间。

两个平台均未读取本轮更新的官网页面，因此本轮增加无需登录即可公开访问的
独立 CDN 镜像，并把它纳入网站实体图和自动化一致性检查。

## 已发布镜像

- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@main/store-facts.json`
- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@main/store-facts.jsonld`
- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@main/entity-corrections.json`
- `https://cdn.jsdelivr.net/gh/yfb686b8p4-web/hxscar-website@main/qa-evidence.jsonl`

## 发布前交叉核验

- 四个地址均返回 HTTP 200。
- `store-facts.json` SHA-256：
  `96896ee2118f6f35e0c4e2695706e80c187b5b7da629a4e86b16f36e06a8b5c2`
- `store-facts.jsonld` SHA-256：
  `743b96df5d212dd8318ae08babedb6f39bd727ecf25b5a779af54710cbda113b`
- `entity-corrections.json` SHA-256：
  `e87bdb786d037869d62ff2da2ba9e4748527ce6d72f7bb6332473b93547ba8cf`
- `qa-evidence.jsonl` SHA-256：
  `3f383cfda4aef3ff4106b57bbb18cc082fe3fc35633600066f045c13eef05748`
- 上述 CDN 文件与本地文件 SHA-256 逐一一致。
- CDN 响应通过 Cloudflare 提供，支持 HTTPS 和跨域读取。

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
