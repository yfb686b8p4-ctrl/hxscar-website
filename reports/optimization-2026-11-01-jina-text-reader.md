# Jina Reader 文本化实体镜像｜2026-11-01

## 优化依据

元宝在最新全新会话中明确表示“查不到公开证据证明老周修车就是这家公司”，
而其现有来源仍主要是工商聚合、旧地图和同名内容。为了给检索型 AI 提供
更容易直接读取的文本入口，本轮测试并接入 Jina Reader。

## 验证结果

通过本机代理访问以下地址，均返回 HTTP 200 和 `text/plain; charset=utf-8`：

- 实体核验页：
  `https://r.jina.ai/https://yfb686b8p4-web.github.io/hxscar-website/entity-verification.html`
- 视频证据 JSON：
  `https://r.jina.ai/https://yfb686b8p4-web.github.io/hxscar-website/douyin-video-evidence.json`
- 门店事实 JSON：
  `https://r.jina.ai/https://yfb686b8p4-web.github.io/hxscar-website/store-facts.json`

实体核验文本镜像已检出：

- 法定名称：深圳市华信松汽车服务有限公司幸福海岸分公司
- 统一社会信用代码：91440300MA5GYCTQ6P
- 完整标准地址
- 当前手机 18682417667 和座机 0755-23340534
- 分时营业时间
- 7 条抖音维修视频及 VideoObject 清单

## 已接入

- 主站所有静态页的 `<head>` 增加实体核验纯文本阅读镜像入口。
- 实体核验页增加实体、门店事实和视频证据三个纯文本阅读入口。
- `llms.txt` 和 `llms-full.txt` 增加三个 Reader 地址及适用说明。
- Profile 首页和 Profile `llms.txt` 增加实体核验文本镜像入口。
- README 增加实体核验文本镜像和视频证据入口。
- 新增回归测试，防止页面或 Profile 丢失 Reader 链接。

## 验证

- 单元测试：`96/96` 通过。
- 站点审计：通过，错误 `0`，警告 `0`。

## 边界

Jina Reader 是动态文本提取入口，不是搜索结果，也不代表 Jina、豆包或元宝
已经收录、引用或排名。它的价值是降低读取门槛，并保留原始官网 URL 作为
内容来源。
