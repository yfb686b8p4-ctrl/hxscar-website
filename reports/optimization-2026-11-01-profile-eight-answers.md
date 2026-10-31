# Profile 八问镜像与 v6 证据同步｜2026-11-01

## 问题

主站已有 16 条原子问答，其中新增了轿之林历史主体消歧；但 Profile Pages
仍只有 7 个直接答案，且多个公开机器入口继续使用“七问”标记。外部镜像因此
缺少当前最重要的实体消歧答案。

## 优化

- Profile `answers.html` 从 7 问扩展到 8 问，新增：
  `幸福海岸花园7栋104、105以前登记的轿之林，和现在的华信松、老周修车是同一家吗？`
- 同步更新 Profile `CollectionPage.numberOfItems`、项目列表、`FAQPage`
  和可见正文。
- Profile 首页增加“同址历史主体”答案范围。
- 主站、Profile 和机器语料中的“七问/七个直接答案”统一改为“八问”。
- 门店事实中的 Profile 镜像名称同步更新。
- 为保持机器事实版本一致，使用新不可变标签
  `ai-evidence-cdn-2026-11-01-v6`。
- 实体核验 PDF 同步更新 v6 镜像地址。

## 验证

- 单元测试：`104/104` 通过。
- 站点审计：通过，错误 `0`。
- Profile `FAQPage.mainEntity`：8 条。
- Profile `CollectionPage.numberOfItems`：8。
- Profile 原子问答证据：16 条。
- PDF：3 页，已重新渲染检查，新 SHA-256
  `2e162eceacbbfe0c4399d3ce8764e0d6c569cacbe181b6aed9025f14ed3b6f8b`。

## 待发布

- 提交主站与 Profile。
- 创建并推送 jsDelivr v6 标签。
- 更新 Release、Gist、Profile Pages 和 PDF Release 附件。
- 完成六方镜像一致性、IndexNow 和线上 URL 验证。
