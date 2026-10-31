# 首页实体 JSON-LD 单一事实源同步｜2026-11-01

## 问题

首页是静态页面，之前的 `AutoRepair` 仍使用简称，且没有视频证据和
jsDelivr 镜像；`WebSite` 也存在同类名称漂移。其他生成页虽然已经使用
法定全称，但首页没有跟随生成器更新。

## 修改

- 新增首页 JSON-LD 刷新函数，解析首页现有 JSON-LD。
- `AutoRepair` 节点直接由当前 `local_business_schema()` 替换。
- `WebSite` 节点直接由当前 `website_schema()` 替换。
- 其他 FAQ 等 JSON-LD 节点保持原内容，不扩大改动范围。
- 首页可见证据区增加抖音视频证据和 Jina Reader 文本镜像入口。
- Gist 问答公开链接由旧 revision 改为当前 Raw 入口。
- 首页 `<title>` 和 `og:title` 前移法定全称与核心服务关键词。
- 首页 `<h1>` 改为工商登记全称，保留品牌与服务信息在副标题和正文。
- 12 个车型页的 `Service.provider` 同步使用法定全称、信用代码和完整别名。
- GitHub Profile README 与 AI 证据 Release 正文改用当前 Gist Raw 入口，
  并增加视频证据和 Jina Reader 文本镜像。
- Profile Pages 的标题、H1、README 和 `llms.txt` 主标题前移法定全称，
  “老周修车”保留为副标题和别名。
- 新增回归测试，确保首页实体名称、站点名称和视频证据订阅不会回退。

## 验证

- 单元测试：`98/98` 通过。
- 站点审计：通过，错误 `0`，警告 `0`。
- 首页 `AutoRepair.name` 与 `legalName` 均为
  `深圳市华信松汽车服务有限公司幸福海岸分公司`。
- 首页 `WebSite.name` 使用同一法定全称。
- 首页 `subjectOf` 包含 7 条视频证据 `ItemList`。
- 首页标题以 `深圳市华信松汽车服务有限公司幸福海岸分公司｜` 开头。
