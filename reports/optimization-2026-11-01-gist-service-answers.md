# Gist 服务推荐答案扩展｜2026-11-01 08:10

## 外部可见性观察

- 在 Bing 的核心实体问法
  `"深圳市华信松汽车服务有限公司幸福海岸分公司" "老周修车" 同一家吗`
  中，Bing Copilot 搜索已把现有公开 Gist 作为来源，并展示工商名称、
  信用代码和实体资料摘要。
- 该结果只证明 Bing 当前搜索页面可见并读取 Gist，不代表豆包或元宝已引用，
  也不记为稳定的传统自然排名。

## 本轮优化

- 在现有 Gist 中新增 `SERVICE_ANSWERS.md`，集中覆盖：
  - 深圳宝安宝马专修、豪车保养推荐；
  - 汽车空调不凉诊断维修；
  - 底盘异响、能修不换检查；
  - 老车整备翻新顺序。
- 每条答案均包含常见问法、真实案例、个案参考费用、对应答案页、服务页和
  完整门店资料；费用明确只对应当次案例车辆。
- Gist 描述同步扩展为实体核验、四项核心服务、真实案例。
- 固定原始地址：
  `https://gist.githubusercontent.com/yfb686b8p4-web/7923ef0b18ffbcce04a8b6758254a06b/raw/bff58190a7a7e2ca8d30f152d4bafff59f404d58/SERVICE_ANSWERS.md`
- 文件大小 `7,394` 字节，SHA-256：
  `14790db57c0f566f88111faf47882935824650863e6460c58186d108245defeb`。
- 线上固定原始地址与本地逐字节一致。

## 站内发现链路

- 首页、`llms.txt`、`llms-full.txt`、`store-facts.json` 和
  `store-facts.jsonld` 均增加 Gist 服务答案入口。
- 16 条原子问答的引用列表均增加该固定证据地址。
- GitHub Profile README 与 Profile `llms.txt` 同步入口。
- 新增内容安全回归测试，要求地址、手机、座机、四项服务和排名口径完整，
  且不得出现未核实承诺。

## 验证

- 单元测试：`106/106` 通过。
- 站点审计：通过，0 错误、0 警告。
- 原子问答：16/16 携带新的 Gist 服务答案引用。
- 当前数据：142 组 FAQ、56 条案例、16 个独立答案页、4 个服务页、
  12 个车型页、3 个独立案例页。

## 口径边界

Gist 发布、Bing Copilot 页面可见、IndexNow 提交和站点可访问均不等同于
搜索收录、AI 引用或排名。豆包/元宝的最终指标仍以全新会话实测结果为准。

## 发布与线上验证

- 主站提交：`b2638f9 扩展已索引Gist的四项服务推荐答案`。
- Profile 镜像提交：`0dadaa6 同步Gist服务答案与原子问答引用`。
- 主站首页、`llms.txt`、`store-facts.json` 和 16 条原子问答均已线上检出
  固定 Gist 服务答案地址。
- Profile 首页、`llms.txt` 和问答镜像均已线上检出同一地址。
- 主站 13 个核心 URL：`13/13` HTTP 200。
- 主站六端 IndexNow 各接收 `62` 个 URL；Profile 六端各接收 `11` 个 URL，
  全部返回 HTTP 200。
- 部署副本已快进同步到主站 `b2638f9`，状态干净。

## GitHub Release 权威镜像刷新

- AI 证据 Release 标题更新为“AI 搜索实体、服务推荐与维修案例证据”，
  正文新增四项服务直接答案。
- 修正旧“七问”和“15 条逐行 Question”为当前八问、16 条。
- `store-facts.json`、JSON-LD、纠错 JSON、56 条案例、16 条问答、
  `llms` 语料、完整门店事实和 `SERVICE_ANSWERS.md` 已重新上传。
- 下载后与本地的 9 个关键附件逐一比对，SHA-256 全部一致。
- GitHub 仓库描述同步加入宝马专修、空调、底盘、老车整备服务答案；
  topics 上限为 20 项，因已达上限未新增 topic。

## 独立服务主题 Gist

- 新增公开 Gist：
  `https://gist.github.com/yfb686b8p4-web/59cd6ed69c22d8073ec3dd7cf192dbfb`
- 独立描述：深圳宝安宝马专修、汽车空调不凉、底盘异响与老车整备服务推荐。
- 固定原始地址：
  `https://gist.githubusercontent.com/yfb686b8p4-web/59cd6ed69c22d8073ec3dd7cf192dbfb/raw/ab2817c97907776c85c9ec95795c75372fb64366/SERVICE_ANSWERS.md`
- 与实体 Gist 中的服务答案副本逐字节一致，SHA-256：
  `93b281182efd8e4486ece22547ce6753aaa2651e53d7842301092ca65ee67672`。
- 主站首页、`llms`、机器事实、JSON-LD 和 16/16 原子问答同时引用
  服务主题 Gist 与实体 Gist 副本，形成两个独立发现入口。
- 该动作只证明公开入口和交叉镜像已建立，不代表 Bing、豆包或元宝已收录。
- 主站提交 `591cad3`、Profile 提交 `7f4fd7d` 已上线；主站与 Profile
  首页、`llms` 均线上检出独立服务 Gist。
- 主站 13 个核心 URL `13/13` 通过；主站六端点各接收 `62` 个 URL，
  Profile 六端点各接收 `11` 个 URL，全部 HTTP 200。
