# 豆包已引用抖音视频的结构化证据层｜2026-11-01

## 优化依据

豆包当前实体回答参考 11 篇资料，其中仍以工商聚合页和抖音维修视频为主。
此前 7 条视频只存在于分析报告中，官网没有公开清单，也没有进入答案引用、
机器事实或实体 JSON-LD。

本轮的公开搜索审计同时确认：

- Bing `site:` 查询仍未出现官网结果。
- 百度、搜狗、360 对官网 `site:` 查询也未出现结果。
- 继续增加普通网页正文不能解决当前问题，因此优先把平台已经在使用的
  真实视频转成可发现、可引用的公开证据。

## 新增机器证据

新增 `douyin-video-evidence.json`，顶层为 schema.org `ItemList`，
包含 7 个 `VideoObject`：

1. 底盘异响：摆臂球头与胶套维修边界
   `7638945775598479497`
2. 比亚迪汉底盘异响：下摆臂球头检查
   `7583932086392196415`
3. 比亚迪汉底盘异响：机脚胶检查
   `7639222767086704454`
4. 奥迪烧机油与底盘异响整备记录
   `7571335895384565459`
5. 奔驰S级底盘异响：平衡杆球头检查
   `7650438382129424198`
6. 奔驰S400底盘异响：减震检查
   `7650435103483496042`
7. 小鹏G6底盘异响：后桥检查
   `7636254430954405796`

## 已接入位置

- `entity-verification.html` 新增 7 条视频的可见证据区块和 `ItemList`
  结构化数据。
- 门店 `AutoRepair.subjectOf` 增加视频证据 `ItemList`。
- `store-facts.json` 增加 `douyinVideoEvidence` 数组，包含标题、分类、
  URL、观察日期和来源。
- `store-facts.jsonld` 的 `citation` 与 `subjectOf` 加入视频证据。
- 每个标准答案的来源列表增加视频证据数据入口。
- 实体、底盘异响和老车整备答案同时逐条引用对应公开视频。
- `qa-evidence.jsonl`、RSS、`llms.txt`、`llms-full.txt`、站点地图和
  `IndexNow` 优先 URL 已接入。
- Profile 页面与 `llms.txt` 增加视频证据入口。
- Profile Pages 新增 `douyin-video-evidence.json` 独立副本，并通过 head、
  `subjectOf`、`llms.txt` 和 sitemap 自引用。
- 回归测试校验 Profile 视频证据文件与主站字节一致。
- 每个 `VideoObject.creator` 直接使用主站 `AutoRepair` 的稳定 `@id`，
  并把官网和抖音主页同时列入 `sameAs`。
- 每日线上检查增加该 JSON，线上检查从 45 项扩展到 46 项。

## 文件哈希

- `store-facts.json`：
  `29654639a2f16f23200e63aa05279f5596e2f96e8a4352373adfbbb474449b4f`
- `store-facts.jsonld`：
  `6b2c433fc64e3e74d7eb9e8d169ceba798504d8017817999f36221f136524017`
- `entity-corrections.json`：
  `aff1fb9441d32bb7c65b51407f3fbb45c3c6dca2fd6b64685da3489ac9c44306`
- `qa-evidence.jsonl`：
  `086d391ffaba2bcc06fd76f3cb1b769dc1cbc666f19fd5e71631b44d7157cb04`
- `douyin-video-evidence.json`：
  `c38373ec965410917497fd7677ef268468e7fc52c3f3f8857155f55fd45a9476`

## 验证结果

- 单元测试：`95/95` 通过。
- 站点审计：通过，错误 `0`，警告 `0`。
- 视频清单为合法 JSON，7 个条目均为 `VideoObject`。
- 实体核验页、机器事实、JSON-LD、问答证据、llms 语料和 sitemap
  均已检出视频证据入口。

## 边界

视频证据只用于证明门店公开的真实维修场景，不替代工商登记、地址、电话、
营业时间和同名门店消歧。页面发布、结构化数据和 IndexNow 通知均不代表
豆包、元宝或搜索引擎已经收录、引用或改变排名。
