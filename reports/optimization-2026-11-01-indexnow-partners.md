# IndexNow 多搜索端点扩展｜2026-11-01

## 已验证端点

使用同一站点验证密钥提交实体核验页，各端点返回：

- IndexNow 聚合端点：HTTP 200
- Bing：HTTP 200
- Yandex：HTTP 202
- Seznam：HTTP 200
- Naver：HTTP 200
- Yep：HTTP 200

## 全量提交

主站已向六个端点提交 60 个优先 URL：

- 聚合、Bing、Yandex、Seznam、Naver、Yep 均返回 HTTP 200。

Profile 已向六个端点提交 11 个 URL：

- 聚合、Bing、Seznam、Naver、Yep 返回 HTTP 200。
- Yandex 返回 HTTP 202，表示请求已接受处理。

## 代码与回归

- `submit_indexnow.py` 的端点列表从 2 个扩展到 6 个。
- Profile 提交脚本复用同一端点列表。
- 新增端点白名单回归测试，防止端点被无意移除或改错。
- 单元测试：`101/101` 通过。

## 边界

HTTP 200/202 只证明搜索端点接收了 IndexNow 请求，不代表已经抓取、收录、
引用或排名。Yandex、Seznam、Naver 和 Yep 的后续可见性仍需独立搜索验证。
