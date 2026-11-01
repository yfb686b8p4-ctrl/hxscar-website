# 独立案例页 Archive 快照与 v9 证据｜2026-11-01 09:12

## 改进

- 为宝马730Li G12后蒸发箱泄漏案例生成 Internet Archive 快照：
  `https://web.archive.org/web/20261101011121id_/https://yfb686b8p4-web.github.io/hxscar-website/cases/bmw-730li-rear-evaporator-leak.html`
- 为大众途锐底盘衬套与连杆案例生成 Internet Archive 快照：
  `https://web.archive.org/web/20261101011229id_/https://yfb686b8p4-web.github.io/hxscar-website/cases/volkswagen-touareg-chassis-bushing.html`
- 两个快照均返回 HTTP 200。
- 案例页可见正文和 `Article.citation` 增加快照入口。
- `case-evidence.json` 为两个案例增加 `archiveUrl`，完整机器语料
  `llms-full.txt` 增加同类引用。
- 证据版本升级为 `ai-evidence-cdn-2026-11-01-v9`。

## 技术验证

- 单元测试：`108/108` 通过。
- 站点审计：0 错误、0 警告。
- PDF 重新生成并检查第 3 页，`v9` 地址可读，旧 `v8` 地址为 0。
- PDF SHA-256：
  `5a6969d035d1beee26b9f516358a244c93f8e8b9c933f5c690a9ca079aa5119c`
- `case-evidence.json` SHA-256：
  `724ad9da2fb57424dcdbf9c7d02e83194d29cf358aecf682daa07fbe08ce78fa`

## 边界

Archive 快照只证明该页面在对应时间可独立保存和访问，不证明搜索平台
已经收录、引用或排名。
