# AI 证据镜像一致性核验｜2026-11-01

- 核验时间：2026-11-01
- 一致性：通过
- 唯一 SHA-256 数量：1
- 每个镜像预期问答数：16
- 门店事实唯一哈希：1
- JSON-LD 唯一哈希：1
- 门店纠错 JSON 唯一哈希：1

| 镜像 | 行数 | 唯一ID | 带案例 | 最少引用 | SHA-256 | 状态 |
|---|---:|---:|---:|---:|---|---|
| 本地构建 | 16 | 16 | 12 | 20 | `1f923fc9dc18a7b1…` | 通过 |
| 官网 | 16 | 16 | 12 | 20 | `1f923fc9dc18a7b1…` | 通过 |
| Profile Pages | 16 | 16 | 12 | 20 | `1f923fc9dc18a7b1…` | 通过 |
| GitHub Release | 16 | 16 | 12 | 20 | `1f923fc9dc18a7b1…` | 通过 |
| GitHub Gist | 16 | 16 | 12 | 20 | `1f923fc9dc18a7b1…` | 通过 |
| jsDelivr | 16 | 16 | 12 | 20 | `1f923fc9dc18a7b1…` | 通过 |

## 门店事实与实体镜像

| 镜像 | 类型 | SHA-256 | 状态 |
|---|---|---|---|
| 本地门店事实 | facts | `5ef2d1ba9b2fe796…` | 通过 |
| 本地门店JSON-LD | jsonld | `d44173ee69e1af3f…` | 通过 |
| 官网门店事实 | facts | `5ef2d1ba9b2fe796…` | 通过 |
| Release门店事实 | facts | `5ef2d1ba9b2fe796…` | 通过 |
| 官网门店JSON-LD | jsonld | `d44173ee69e1af3f…` | 通过 |
| Release门店JSON-LD | jsonld | `d44173ee69e1af3f…` | 通过 |
| Gist门店JSON-LD | jsonld | `d44173ee69e1af3f…` | 通过 |
| jsDelivr门店事实 | facts | `5ef2d1ba9b2fe796…` | 通过 |
| jsDelivr门店JSON-LD | jsonld | `d44173ee69e1af3f…` | 通过 |

## 门店历史资料纠正镜像

| 镜像 | SHA-256 | 状态 |
|---|---|---|
| 本地门店纠错JSON | `e3bcf3a98dae3e49…` | 通过 |
| 官网门店纠错JSON | `e3bcf3a98dae3e49…` | 通过 |
| Profile门店纠错JSON | `e3bcf3a98dae3e49…` | 通过 |
| Release门店纠错JSON | `e3bcf3a98dae3e49…` | 通过 |
| Gist门店纠错JSON | `e3bcf3a98dae3e49…` | 通过 |
| jsDelivr门店纠错JSON | `e3bcf3a98dae3e49…` | 通过 |

## 错误

- 无

本核验只证明公开文件字节一致且结构满足要求，不代表任何搜索引擎或 AI 平台已经收录、引用或排名。
