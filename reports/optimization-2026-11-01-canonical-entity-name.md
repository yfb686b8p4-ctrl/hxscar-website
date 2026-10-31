# 法定代表人名称与品牌别名统一｜2026-11-01

## 优化依据

元宝在实体问题中仍把工商登记主体、品牌简称和同名门店混为不同对象。
公开搜索复查同时显示，Bing 对以下精确查询均返回 0 条结果：

- `site:yfb686b8p4-web.github.io/hxscar-website`
- `"91440300MA5GYCTQ6P"`
- `"老周修车" "幸福海岸"`

因此本轮不重复堆叠关键词，而是修正机器可读实体主名称，使结构化数据与
工商登记名称逐字一致，同时保留用户熟悉的品牌别名。

## 已执行

- `AutoRepair.name` 和 `AutoRepair.legalName` 统一为
  `深圳市华信松汽车服务有限公司幸福海岸分公司`。
- `WebSite.name` 同步使用法定全称。
- `store-facts.json` 的 `entity.canonicalName` 使用法定全称。
- 新增 `entity.displayName`，保留
  `华信松汽车服务有限公司（幸福海岸分公司）` 作为对外展示名称。
- `alternateName` 与 `entity.aliases` 继续保留 `老周修车`、
  `驰加米其林幸福海岸店`、`宝源南路店`、`艾德养车（幸福海岸店）` 等
  已核验别名。
- 服务页和车型页内嵌的门店 `provider` 同步补充法定全称、信用代码和
  完整别名集合。
- RSS 门店事实同时区分法定名称与对外展示名称。
- Profile Pages 的 `AutoRepair.name`、`WebSite.name` 和
  `entity-corrections.json` 同步使用法定全称。
- Profile `FAQPage` 删除重复问法，把第二个标准资料问题改为工商全称问法。

## 验证结果

- 单元测试：`94/94` 通过。
- 站点审计：通过，错误 `0`，警告 `0`。
- 生成范围：15 个答案页、4 个服务页、12 个车型页、3 个独立案例页。
- `store-facts.jsonld` 可解析，`taxID` 为 `91440300MA5GYCTQ6P`。
- `entity-corrections.json` 的 `canonicalName` 与工商登记名称一致。
- 主站 Pages `620ae89` 构建成功。
- Profile Pages `5665b1a` 构建成功。
- 线上 `store-facts.json` 已检出法定全称、展示名称和 6 个已核验别名。
- 线上 `store-facts.jsonld` 已检出法定全称与
  `91440300MA5GYCTQ6P`。
- IndexNow 聚合端点和 Bing 直连端点均返回 HTTP 200：
  主站 59 个 URL，Profile 10 个 URL。

## 边界

本轮只证明实体主名称已在站内页面和机器文件中统一，并通过本地结构检查。
尚未观察到 Bing、豆包或元宝因此重新抓取、收录、引用或改变排名。
