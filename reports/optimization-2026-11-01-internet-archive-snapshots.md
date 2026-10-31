# Internet Archive 实体快照｜2026-11-01

## 已创建快照

- 实体核验页：
  `https://web.archive.org/web/20261031222738id_/https://yfb686b8p4-web.github.io/hxscar-website/entity-verification.html`
- 门店机器事实：
  `https://web.archive.org/web/20261031222736id_/https://yfb686b8p4-web.github.io/hxscar-website/store-facts.json`

## 保真核验

- 两个快照均返回 HTTP 200。
- 实体核验页快照与本地文件 SHA-256 完全一致：
  `36c8e2ddaca4fab34bbe97505e489a446485fce1914350af64f08a52893b50e2`
- 门店事实快照与本地文件 SHA-256 完全一致：
  `29654639a2f16f23200e63aa05279f5596e2f96e8a4352373adfbbb474449b4f`
- 快照正文包含法定名称、信用代码、完整地址、双电话、分时营业时间和
  7 条视频证据。

## 已接入

- 主站所有生成页的 head 增加实体核验 Archive 快照发现入口。
- 实体核验页增加实体页和机器事实两个 Archive 快照链接。
- 主站 `llms.txt`、`llms-full.txt`、README 和 AI 证据 Release 正文增加快照地址。
- Profile 首页与 `llms.txt` 增加 Archive 入口。

## 边界

当前运行环境直连 `web.archive.org` 会超时，通过本机代理可正常读取。
因此没有把 Archive 加入每日自动健康检查，避免把网络可达性误报成页面故障。
快照存在不等于 Archive 页面被搜索引擎收录，也不代表豆包或元宝已引用。
