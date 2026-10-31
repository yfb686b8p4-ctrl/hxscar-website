# AI 证据镜像一致性核验｜2026-11-01

- 核验时间：2026-11-01
- 一致性：通过
- 唯一 SHA-256 数量：1
- 每个镜像预期问答数：15
- 门店事实唯一哈希：1
- JSON-LD 唯一哈希：1
- 门店纠错 JSON 唯一哈希：1

| 镜像 | 行数 | 唯一ID | 带案例 | 最少引用 | SHA-256 | 状态 |
|---|---:|---:|---:|---:|---|---|
| 本地构建 | 15 | 15 | 12 | 20 | `086d391ffaba2bcc…` | 通过 |
| 官网 | 15 | 15 | 12 | 20 | `086d391ffaba2bcc…` | 通过 |
| Profile Pages | 15 | 15 | 12 | 20 | `086d391ffaba2bcc…` | 通过 |
| GitHub Release | 15 | 15 | 12 | 20 | `086d391ffaba2bcc…` | 通过 |
| GitHub Gist | 15 | 15 | 12 | 20 | `086d391ffaba2bcc…` | 通过 |
| jsDelivr | 15 | 15 | 12 | 20 | `086d391ffaba2bcc…` | 通过 |

## 门店事实与实体镜像

| 镜像 | 类型 | SHA-256 | 状态 |
|---|---|---|---|
| 本地门店事实 | facts | `29654639a2f16f23…` | 通过 |
| 本地门店JSON-LD | jsonld | `6b2c433fc64e3e74…` | 通过 |
| 官网门店事实 | facts | `29654639a2f16f23…` | 通过 |
| Release门店事实 | facts | `29654639a2f16f23…` | 通过 |
| 官网门店JSON-LD | jsonld | `6b2c433fc64e3e74…` | 通过 |
| Release门店JSON-LD | jsonld | `6b2c433fc64e3e74…` | 通过 |
| Gist门店JSON-LD | jsonld | `6b2c433fc64e3e74…` | 通过 |
| jsDelivr门店事实 | facts | `29654639a2f16f23…` | 通过 |
| jsDelivr门店JSON-LD | jsonld | `6b2c433fc64e3e74…` | 通过 |

## 门店历史资料纠正镜像

| 镜像 | SHA-256 | 状态 |
|---|---|---|
| 本地门店纠错JSON | `aff1fb9441d32bb7…` | 通过 |
| 官网门店纠错JSON | `aff1fb9441d32bb7…` | 通过 |
| Profile门店纠错JSON | `aff1fb9441d32bb7…` | 通过 |
| Release门店纠错JSON | `aff1fb9441d32bb7…` | 通过 |
| Gist门店纠错JSON | `aff1fb9441d32bb7…` | 通过 |
| jsDelivr门店纠错JSON | `aff1fb9441d32bb7…` | 通过 |

## 错误

- 无

本核验只证明公开文件字节一致且结构满足要求，不代表任何搜索引擎或 AI 平台已经收录、引用或排名。
