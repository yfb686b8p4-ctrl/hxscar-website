# 搜索索引状态检查｜2026-11-01 00:04

## 08:45 AI 搜索证据政策页

- 新增 `evidence-policy.html`，公开五级证据优先级、同址历史主体处理、
  历史电话纠错和“提交不等于收录/引用/排名”的口径。
- 页面加入全站导航、`sitemap.xml`、`llms.txt`、`llms-full.txt` 和
  IndexNow 优先 URL；每日检查新增该页面。
- 当前单元测试 104/104、站点审计通过；线上验证与 IndexNow 提交将在部署后
  执行。

## 08:30 实体核验 PDF 更新

- 3 页 PDF 已加入轿之林历史个体户、当前双电话、旧号码纠错和第三方状态
  字段冲突说明。
- PDF SHA-256：
  `0adbd6d391c32bb5f039029f8653478eb5c860f1660a0a1e7439bbb418a28b73`。
- GitHub Release PDF 附件已替换并逐字节一致；主站 Pages `c92b3ff`
  deploy 成功后，线上附件与本地文件逐字节一致，13/13 核心 URL 通过。
- PDF 文本和页面渲染均已检查，无裁切、重叠、乱码或黑块。

## 08:20 证据链接代理回退审计

- 证据链接审计器新增“直连超时后经本地代理重试”，避免把暂时网络失败
  误报成坏链；新增回归测试，当前单元测试 103/103 通过。
- 重新审计 8 个机器证据文件中的 162 个唯一 URL：
  - 152 个 HTTP 200；
  - 10 个平台防抓/限流；
  - 0 个确认坏链。
- Jina、Internet Archive 和企查查的无响应/405 继续按平台防抓记录，
  不据此判断页面失效。
- 该结果只证明证据链接当时可解析，不代表搜索收录、AI 引用或排名。

## 08:05 轿之林 v5 与 Release 可见正文

- 主站 `9df1e68` 与 Profile `39624a6` 的 Pages build/deploy 均成功。
- 主站核心 URL 13/13 通过；主站六端点各接收 61 个 URL，Profile 六端点
  各接收 11 个 URL。
- GitHub Release、Gist、Profile Pages 与 jsDelivr v5 字节一致；六方问答
  镜像一致性恢复通过，16 行、16 个唯一 ID。
- GitHub AI 证据 Release 的可见正文已更新为完整门店事实页，并检出
  `92440300MA5F133M2E`、当前手机 `18682417667` 和状态字段冲突说明。
- 元宝精确消歧复测仍能区分旧、新信用代码，但仍不认可老周修车与当前门店
  的公开关系，并继续使用旧电话；该结果仍为部分正确，不是核心护栏通过。

## 07:55 轿之林精确消歧 v5

- 主站新增轿之林历史个体户信用代码 `92440300MA5F133M2E` 与当前华信松
  `91440300MA5GYCTQ6P` 的独立答案，机器事实同步说明第三方“注销/在业”
  状态字段冲突，最终以国家企业信用信息公示系统为准。
- 主站与 jsDelivr 使用不可变标签 `ai-evidence-cdn-2026-11-01-v5`；
  Release、Gist、Profile Pages 和六方问答镜像同步后再执行 IndexNow。
- 元宝上线后复测仍能区分两个历史信用代码，但仍不认可“老周修车是当前
  华信松门店对外称呼”，继续使用旧电话，因此不能记为完整改善。

## 07:35 元宝旧营业时间专项与 Sogou 公开发现入口

- 元宝“营业时间08:00-20:00、地址电话”专项复测参考 8 篇资料，仍返回
  腾讯地图旧地址/旧时段和企百科 2024 年报电话，未读取官网纠错页。
- GitHub 主仓库与 Profile 仓库描述已补入“同一地址历史主体消歧、地址电话
  营业时间纠错”，主仓库新增 `entity-resolution` topic；Gist 描述同步为
  精确门店实体问题。
- Sogou 存在公开“网站收录/申诉”说明页，写明一次提交一个完整 URL、
  20-30 个工作日观察期且不保证收录；当前抓取页面未显示可提交表单，
  不记为已提交。账号本人仍需从可交互页面完成验证或使用站长平台 sitemap。
- 本轮仍没有 Sogou、Baidu、头条收录或引用证据，不能把外部元数据更新写成
  排名提升。

## 07:20 同址历史主体消歧 v3 镜像

- 新增独立答案页 `answers/same-address-history.html`，标准答案从 15 条增至
  16 条，搜狗立知申请包同步为 93 条问答。
- 主站最终部署提交 `3f9d5eb` 的 build 与 deploy 均成功，线上核心 URL
  13/13 返回 HTTP 200。
- GitHub Release、Gist、Profile Pages 与 jsDelivr v3 已同步；六方问答镜像
  一致性检查通过，16 行、16 个唯一 ID。
- 主站 IndexNow 六端点均接收 61 个 URL；Profile 六端点均接收 11 个 URL。
- 元宝同址历史主体专项复测已能区分旧主体和当前主体，但普通核心问法仍
  使用旧营业时间，且 34 篇来源仍未读取本店官网。
- IndexNow、Release 与 jsDelivr 成功只证明提交、发布和可访问，不证明收录、
  引用或排名。

## 06:47 多端 IndexNow、Archive 与引用 URL 审计

- IndexNow 已从聚合端点与 Bing 扩展到 Yandex、Seznam、Naver、Yep。
- 主站向六个端点提交 60 个 URL，全部返回 HTTP 200。
- Profile 向六个端点提交 11 个 URL，全部返回 HTTP 200/202。
- 机器问答、案例、门店事实、纠错、视频与机器语料共提取 160 个唯一 URL：
  156 个直接返回 HTTP 200，4 个被平台防抓/限流，无 404 坏链。
- Internet Archive 已保存实体核验页、门店事实、实体关系答案、视频证据和
  首页服务快照；`id_` 原始快照与对应本地文件 SHA-256 逐一一致。
- Seznam 查询当前返回 `totalResults: 0`，Naver 显示无搜索结果。
- Yandex 触发 SmartCaptcha，Yep 返回 HTTP 403，无法读取结果；不据此判断
  “未收录”。
- 以上状态只证明提交、可访问和保存成功，不证明已收录、引用或排名。

## 04:27 四镜像一致性与搜狗入口复核

- 新增 `scripts/verify_ai_evidence_mirrors.py`，同时核验官网、Profile Pages、GitHub Release 和 Gist 的 `qa-evidence.jsonl`。
- 四个镜像当前均为 15 行、15 个唯一 ID、12 条关联真实案例、最少 15 个引用，SHA-256 均为 `3f383cfda4aef3ff4106b57bbb18cc082fe3fc35633600066f045c13eef05748`。
- 每日线上检查从 30 项扩展为 32 项，新增 Release 和 Gist 问答镜像检查；当前 89 项单元测试通过，站点审计通过。
- 搜狗资源平台未发现可靠的匿名 sitemap ping 接口；站点验证和 sitemap 提交仍需登录，立知合作仍以 `zzpt@tencent.com` 邮件申请为入口。

## 04:23 Profile镜像与GitHub发现信号

- Profile 仓库提交 `614fc84` 已上线，首页增加 4 项 `OfferCatalog`、4 个服务区域和重点车型实体，五问页与 `llms.txt` 增加原子问答入口。
- Profile 后续提交 `8aeef90` 在根路径发布 `qa-evidence.jsonl` 镜像，线上 SHA-256 与官网一致，sitemap 和 `llms.txt` 已同步。
- Profile 线上已检出 `OfferCatalog`、4 个服务区域、13 个重点车型和 QA 链接；Profile IndexNow 5 个 URL 在聚合端点与 Bing 直连端点均返回 HTTP 200。
- 两个 GitHub 仓库的 topics 已扩展为 19 项，新增 `bmw-repair`、`car-air-conditioning`、`chassis-repair`、`vehicle-restoration`、`entity-verification`、`ai-evidence`、`jsonl` 和 `knowledge-graph`。
- Gist 描述已更新为门店实体、真实维修案例与 15 条原子问答证据。
- 当前 89 项单元测试通过，站点审计通过。

## 04:20 原子问答证据数据

- 新增 `qa-evidence.jsonl`，每行一条 schema.org `Question`，共 15 条标准问答，每条包含直接答案、真实案例和逐答案引用。
- 15 条问答中 12 条关联真实维修案例；每条答案当前包含 15 个 HTTPS 引用，最少 4 个的审计下限已满足。
- 首页、全部答案/服务/车型/案例页通过 `<link rel="alternate" type="application/x-ndjson">` 声明数据入口。
- `sitemap.xml`、`llms.txt`、`llms-full.txt`、`store-facts.json` 和 `store-facts.jsonld` 已链接该文件。
- Gist 已新增 `qa-evidence.jsonl` 镜像，不可变 Raw revision 的 SHA-256 与官网文件一致。
- 每日线上检查从 28 项扩展为 29 项；当前 84 项单元测试通过，站点审计通过。
- 该动作只证明数据已生成且可发现，尚未被 Bing、百度、豆包、元宝或其他平台抓取或引用。

## 04:04 高意图答案增强与元宝复测

- 提交 `29b4281` 已上线，宝马、宝马5系、底盘异响和老车整备四个答案页各增加 5 步可执行流程、安全边界和带 15 个 HTTPS 来源的 `HowTo` 数据。
- 线上四页均检出对应流程标题、步骤、引用和真实案例；IndexNow 聚合端点与 Bing 直连端点对 53 个 URL 返回 HTTP 200。
- 豆包在“深圳宝安宝马专修 豪车保养 推荐”全新会话中仍将本店列为第 1 项，参考 17 篇资料；该结果不能记为本次新增排名。
- 元宝同一问题参考 15 篇资料，推荐宝盛、宝粤、华胜和宝盈，未提及本店；新增官网正文尚未成为有效候选来源。
- 当前 82 项单元测试通过，站点审计通过。

## 04:10 搜狗立知TOP1问答申请包

- 已确认搜狗资源平台公开招募立知TOP1问答合作，邮件提交至 `zzpt@tencent.com`，官方说明评估期为 7-10 个自然日。
- 已生成 15 条标准答案、84 条安全FAQ、56 条真实案例和 SHA-256 清单，共 99 条问答、56 条案例。
- 申请包位于 `publishing/lizhi/2026-11-01/`，状态为“已准备、尚未发送”。
- 该动作只证明申请材料已完成；不代表腾讯已受理、合作、收录或获得搜索结果首位。

## 01:01 增量提交

- 提交 `ff8fccb` 已推送到 GitHub `main`，线上空调温差答案已检出“更换右温度风门电机”案例正文，`store-facts.json` 同时检出该案例证据。
- IndexNow 聚合端点和 Bing 直连端点再次提交 34 个 URL，均返回 HTTP 200。
- 发布后豆包、元宝全新会话复测同一问题，两个平台仍未提及本店，详见 `reports/recheck-2026-11-01-post-aircon-case.md`。
- 本次提交只证明搜索引擎已收到更新通知；是否抓取、收录、引用或排名仍需后续公开结果验证。

## 01:18 深度优化提交

- 提交 `7c4d44e` 已推送到 GitHub `main`，线上答案已检出“先做 5 项交叉检查”和 5 步 `HowTo` 结构化数据。
- 该页可见中文字符由 879 增至 1579，新增症状分流、冷媒检漏顺序和更换总成安全边界。
- IndexNow 聚合端点和 Bing 直连端点再次提交 34 个 URL，均返回 HTTP 200。

## 01:10 实体资料复测

- 提交 `9a756b6` 已上线，实体核验页首屏和首个 FAQ 同时包含信用代码、标准地址、手机、座机和营业时间。
- 元宝全新会话由优化前的“大概率两家店、旧年报电话”改善为“基本可以确定是同一家店”，并给出正确手机和信用代码。
- 元宝仍未完整给出标准地址、座机和当前营业时间；完整资料不能记为通过，详见 `reports/recheck-2026-11-01-post-entity-facts.md`。

## 01:24 旧营业时间纠错页

- 提交 `962e027` 已上线独立答案页 `answers/contact-correction.html`，直接回答“08:00-20:00 是否准确”，并同时列出当前营业时间、手机、座机、标准地址和历史错误资料。
- 答案索引、RSS、机器事实、`llms.txt`、`llms-full.txt` 和 sitemap 已同步增加该页面。
- IndexNow 聚合端点和 Bing 直连端点提交 35 个 URL，均返回 HTTP 200。

## 01:28 案例与答案双向链路

- 提交 `ff25ea1` 已上线，真实维修案例会按故障类型反链到最相关答案页；奔驰 E300L 右左温差案例已链接到空调温差、空调诊断和服务专题。
- 本次共为空调、底盘、烧机油等真实案例增加 40 条相关答案入口，强化“案例证据 → 故障答案 → 门店事实”的站内链路。
- IndexNow 聚合端点和 Bing 直连端点再次提交 35 个 URL，均返回 HTTP 200。

## 01:32 外部权威镜像同步

- GitHub 提交 `4a2022c` 已上线，`ENTITY_FACTS.md` 和 Release 正文补齐 `13537862708`、旧营业时间与 `contact-correction.html` 纠错入口。
- 现有公开 Gist 与 GitHub Release 均已通过 API 检出更新后的完整门店事实。
- Bing 精确查询 Gist ID 仍显示无相关结果；只能记为“外部镜像已更新”，不能写成“已被 Bing 收录”。

## 01:35 独立真实案例页

- 提交 `53457ea` 已上线 3 个独立案例页：宝马 X5 E70 烧机油、宝马 530Li 底盘异响、奔驰 E300L 空调左右温差。
- 三页均通过线上验证，包含 `Article`、`BreadcrumbList`、完整门店资料及对应答案/服务专题链接。
- 空调温差答案的案例引用已从长列表锚点升级为独立案例 URL，案例库和机器语料同步更新。
- IndexNow 聚合端点和 Bing 直连端点提交 38 个 URL，均返回 HTTP 200。

## 01:38 案例语义增强

- 提交 `c5ced5a` 已上线，3 个独立案例页的 `Article` 数据补充车型、故障类型、真实问法关键词和 `speakable` 区块。
- 线上已检出奔驰 E300L 案例的“空调一边冷一边热”关键词及 `Car` 实体。
- IndexNow 聚合端点和 Bing 直连端点再次提交 38 个 URL，均返回 HTTP 200。

## 01:40 案例 RSS 分发

- 提交 `589def7` 已上线，标准 RSS 新增 3 个独立真实案例条目，并携带故障表现、处理过程、费用、门店事实和证据链接。
- 线上 `feed.xml` 已检出奔驰 E300L 独立案例 URL。
- IndexNow 聚合端点和 Bing 直连端点再次提交 38 个 URL，均返回 HTTP 200。

## 01:49 独立 Schema.org 门店实体

- 提交 `b264086` 已上线 `store-facts.jsonld`，包含 `AutoRepair` 实体、工商代码、标准地址、手机、座机、分时营业时间、地图 POI、服务范围和历史字段纠错。
- 全站页面 `<head>`、sitemap、RSS 答案证据、llms 语料和机器事实均增加 JSON-LD 入口。
- 线上文件已通过 JSON 解析与 `AutoRepair`、统一社会信用代码校验。
- IndexNow 聚合端点和 Bing 直连端点提交 39 个 URL，均返回 HTTP 200。

## 01:51 结构化维修案例证据

- 提交 `e6abd4d` 已上线 `case-evidence.json`，覆盖 56 个真实维修案例，包含车型、服务类型、故障表现、处理方案、参考费用、证据 URL 和关联答案 URL。
- 文件明确标注费用与方案仅对应当前案例车辆，其他车辆须先诊断。
- 维修案例页、答案证据、机器事实、sitemap、RSS 和 llms 语料已接入该数据文件。
- 线上已验证 `caseCount=56` 且案例数组完整。
- IndexNow 聚合端点和 Bing 直连端点提交 40 个 URL，均返回 HTTP 200。

## 01:55 案例文章与证据集合关联

- 提交 `38660dc` 已上线，3 个独立案例页的 `Article.isPartOf` 已指向案例 `CollectionPage`，`citation` 已加入 `case-evidence.json`。
- 全站页面均声明 `case-evidence.json` alternate 数据入口，线上案例页已完成验证。
- IndexNow 聚合端点和 Bing 直连端点再次提交 40 个 URL，均返回 HTTP 200。

## 01:58 案例证据升级为 JSON-LD

- 提交 `221d2ee` 已上线，`case-evidence.json` 顶层升级为 schema.org `ItemList`，56 条案例均以 `Article` 条目表达。
- 案例文章的车型 `Car`、标题、正文、费用和关键词均已进入 JSON-LD，现有自定义字段继续保留供普通程序读取。
- 全站 alternate 声明、案例 Article 引用和门店 JSON-LD 的 `subjectOf` 已同步关联该文件。
- 线上已验证 `ItemList`、56 条目和重点 `Article` 条目。
- IndexNow 聚合端点和 Bing 直连端点再次提交 40 个 URL，均返回 HTTP 200。

## 02:01 GitHub Gist 外部镜像

- 现有公开 Gist 已新增 `store-facts.jsonld` 和 `case-evidence.json` 两个文件，并更新文件描述。
- GitHub API 已验证 Gist 中的门店实体为 `AutoRepair`、信用代码为 `91440300MA5GYCTQ6P`、手机为 `18682417667`。
- GitHub API 已验证 Gist 案例数据为 `ItemList`、包含 56 个条目，并保留奔驰 E300L 独立案例 URL。
- 该动作只证明外部镜像已公开；尚未观察到 Bing 收录或 AI 平台引用。

## 02:06 Gist 镜像双向关联

- 提交 `0dbb31f` 已上线，官网与机器事实新增两个稳定 Gist Raw URL：门店 JSON-LD 和 56 条案例 JSON-LD。
- 两个外部镜像已加入门店 `subjectOf`、答案证据来源、README 和 llms 索引。
- 线上门店 JSON-LD 已检出 Gist 镜像地址。
- IndexNow 聚合端点和 Bing 直连端点提交 40 个 URL，均返回 HTTP 200。

## 02:15 GitHub 账号级资料

- 已创建并发布公开仓库 `yfb686b8p4-web/yfb686b8p4-web`，其 README 会显示在 GitHub 账号主页。
- Profile README 已包含标准门店资料、官网、实体 JSON-LD、56 条案例数据、Release、Gist、抖音和地图核验入口。
- GitHub API 已检出公开 Profile README 内容；仓库为 Public，已设置 `auto-repair`、`car-service`、`shenzhen`、`baoan`、`local-seo` 主题。
- 官网主页 JSON-LD 已把 Profile 仓库加入 `sameAs`；GitHub Pages 构建完成并线上检出该链接。
- IndexNow 聚合端点和 Bing 直连端点再次提交 40 个 URL，均返回 HTTP 200。

## 02:19 GitHub 仓库发现信号

- Profile 仓库 Homepage 已设置为官网地址，仓库元数据现在直接指向门店站点。
- Profile 仓库和官网仓库均增加 `structured-data`、`schema-org`、`llms-txt`、`ai-search` 主题。
- GitHub API 已复核 Homepage 和主题设置；仍需继续观察 Bing 收录，当前不能记为搜索可见。

## 02:39 索引入口与全站实体同步

- 提交 `6c2284e` 已上线统一 `sitemap-index.xml`，同时列出内容站点地图和图片站点地图；`robots.txt` 已声明该索引。
- 提交 `8b4259c` 已重跑服务与车型内容生成器，18 个服务/车型页的 `AutoRepair` 结构化数据均补齐 GitHub Profile 的 `sameAs`，并增加审计与单元测试防止回退。
- 提交 `caab517` 已上线修正后的 IndexNow 选择器，服务详情页和 12 个车型详情页现在都进入快速收录通知范围。
- 提交 `09b0a29` 已把 3 条未命中的护栏问法逐字写入对应答案页的可见“常见问法”、`keywords`、机器事实和完整语料，并增加回归测试。
- 公开 Gist 的 `store-facts.jsonld` 与 `ENTITY_FACTS.md` 已同步 GitHub Profile；Raw 地址验证门店 `sameAs` 含该 Profile，共 9 个外部关联。
- GitHub Profile README 已更新到远端提交 `9de0351`，新增宝马、空调、底盘、老车整备和实体关系 5 组直接答案与证据入口。
- 提交 `1780f85` 已把上述 Profile 模板和回归测试归档到官网仓库；源仓库与部署副本均与远端 `main` 同步。
- 当前 65 项单元测试通过，站点审计通过，线上 21 个检查地址 21/21 可访问。
- IndexNow 聚合端点和 Bing 直连端点均对 53 个 URL 返回 HTTP 200。
- Bing 对官网域名、GitHub Profile、Gist 和统一社会信用代码的公开查询仍未检出目标结果；本轮只能记为“已发布并已提交抓取”，不能记为“已收录、已引用或已排名”。

## 03:04 机器语料安全分层与百度推送复核

- 提交 `f945cc9` 已上线 FAQ 安全分层：人工问题库保留 142 组，FAQ 结构化数据和机器语料只使用 97 组不含待核验价格、质保、设备型号、优惠时效或服务台次承诺的问答。
- 其余 45 组 FAQ 已从机器语料排除并标注为待门店确认，人工 FAQ 页面仍保留供查阅。
- 首页 JSON-LD 已移除错误的 `parentOrganization` 品牌隶属断言。
- 提交 `1e37b14` 已同步每日监测器的新机器语料标记；线上 21 个检查地址恢复为 21/21。
- 4 个服务专题页已增加统一的 5 步 `HowTo` 接车流程，覆盖故障说明、检查诊断、维修边界、项目费用确认和复检交付，便于 AI 直接抽取步骤。
- 当前 77 项单元测试通过，站点审计通过；IndexNow 两个端点再次对 53 个 URL 返回 HTTP 200。
- 53 个优先 URL 独立可达性检查为 53/53 HTTP 200。
- 百度旧版 sitemap ping 接口返回 HTTP 404，普通 URL 推送接口在无 token 时返回 HTTP 400。百度资源平台仍需要账号本人完成站点验证、获取推送 token 或提交 sitemap。
- 本节不改变排名指标；当前仍不能声称 Bing、百度或任一 AI 平台已经收录或引用新页面。

## 03:20 AI 证据 Release

- 已发布公开 Release `ai-evidence-2026-11-01`，包含 `store-facts.json`、`store-facts.jsonld`、`case-evidence.json`、`llms.txt` 和 `llms-full.txt` 五个附件。
- 五个附件下载地址均验证为 HTTP 200。
- 官网首页、答案页、服务页、车型页、门店机器事实和 JSON-LD 已加入 Release 页面或附件镜像。
- GitHub Profile 与 Gist 已同步加入 Release 入口；Gist 的门店 JSON-LD 通过 `subjectOf` 关联 3 个 Release 数据附件。
- 该动作只证明外部证据镜像已公开并可下载，不证明任何搜索引擎或 AI 平台已收录、引用或排名。

## 03:35 GitHub Profile 实体镜像页

- 已启用 `https://yfb686b8p4-web.github.io/yfb686b8p4-web/`，GitHub Pages 状态为 `built`。
- 页面首页、`robots.txt`、`sitemap.xml` 和 `llms.txt` 均验证为 HTTP 200。
- 页面包含统一社会信用代码、完整标准资料、实体消歧、五个核心答案入口和 AI 证据 Release。
- 官网、Profile README、Gist 与 Release `store-facts.jsonld` 已相互关联该 Profile Pages。
- Profile 子路径已配置独立 IndexNow key；聚合端点与 Bing 直连端点最终均对 3 个 Profile URL 返回 HTTP 200。
- 2026-11-01 03:22 复核 Bing RSS，Profile Pages、官网域名及“信用代码 + 老周修车”组合均返回 0 条结果，尚未观察到收录。
- 当前 77 项单元测试通过，站点审计通过；该页面是否被搜索或 AI 平台收录仍需后续公开结果验证。

## 03:40 服务型答案补充 Service 实体

- 12 个宝马、空调、底盘和老车整备答案页新增与类别匹配的 `Service` 结构化数据。
- 每个 Service 均关联同一 `AutoRepair` 门店、宝安服务区域、对应服务专题和更新时间。
- 实体关系、标准联系方式和营业时间等 3 个非服务答案页不添加 Service，避免把资料说明误标为服务。

## 03:30 首屏门头图响应式优化

- 新增 `store-banner-960.jpg`，尺寸 960×540，文件约 150 KB，比原始 1,291×726、约 327 KB 的门头图减少约 54%。
- 首页使用 `srcset`、`sizes`、固定宽高、`fetchpriority="high"` 和异步解码，移动端优先加载小图，桌面与 Open Graph 保留原图。
- 新增回归测试，防止首页重新退化为只加载大图。

## 03:23 统一监测主站与 Profile 镜像

- 每日检查从主站 21 项扩展为 26 项，新增 Profile 首页、robots、sitemap、llms 和独立 IndexNow 验证文件。
- 最新检查结果为 26/26 通过。
- Profile Pages 和主站可以分别用独立 IndexNow key 提交，避免再次出现跨路径 HTTP 422。

## 03:33 图片与 27 项运行监测

- 首页 960×540 响应式门头图已上线，线上实测约 153 KB，原图约 335 KB。
- 首页已检出 `srcset`、固定宽高、`fetchpriority="high"` 和 head 预加载。
- 每日检查增加响应式外观图，当前主站与 Profile 镜像统一检查为 27/27 通过。

## 03:44 Profile 五问答案页

- Profile 镜像新增独立 `answers.html`，覆盖宝马、空调、底盘、老车整备和实体关系五个直接答案。
- 页面包含 5 条 `FAQPage` 问答、官网完整答案引用、标准地址、电话、营业时间和统一社会信用代码。
- Profile sitemap、llms 和首页已加入新页面入口。
- Profile 独立 IndexNow 现在提交 4 个 URL，聚合端点和 Bing 直连端点均返回 HTTP 200。
- 统一每日检查扩展为 28 项，当前 28/28 通过；77 项单元测试通过。

## 03:52 Profile 五问答案镜像双向关联

- Profile `answers.html` 已加入官网机器事实、`store-facts.jsonld` 的 `subjectOf`、全部答案证据来源、首页、RSS、`llms.txt` 和 `llms-full.txt`。
- 主站现在可以从多个机器入口直接发现 Profile 五问答案页，不再只依赖 Profile 首页链接。
- Profile 五问页继续作为独立外部镜像，不替代主站 canonical 答案页。
- 当前 77 项单元测试和站点审计通过。

## 已执行

- 官网、答案集群、门店事实、PDF、服务页和车型页共 34 个 URL 已同时提交到 IndexNow 聚合端点和 Bing 直连端点，两个端点均返回 HTTP 200。
- GitHub Pages 和 GitHub Release 当前均可公开访问。
- 11 月 1 日每日检测计划和 12 项结果模板已生成。

## 本次查询

### Bing

- `site:yfb686b8p4-web.github.io/hxscar-website`：结果页未提取到该官网引用。
- `"91440300MA5GYCTQ6P"`：结果页未提取到官网或 GitHub Release 引用。

### 百度

- `site:yfb686b8p4-web.github.io/hxscar-website`：页面未出现该官网域名。
- `"91440300MA5GYCTQ6P"`：页面未出现官网或 GitHub Release 域名。

## 结论

- 当前只能证明 URL 已提交且页面可访问，不能证明已被 Bing 或百度收录。
- 公开搜索结果中尚未检出官网、独立答案页或 GitHub Release 被搜索引擎列为结果。
- IndexNow 提交成功不等于收录、引用或排名。

## 下一步

- 优先完成 Bing Webmaster Tools 和百度搜索资源平台的站点验证、sitemap 提交与抓取诊断。
- 继续观察 Release、Gist 和独立答案页是否进入搜索索引。
- 在搜索平台产生真实收录结果前，不把“已提交”写成“已排名”。
