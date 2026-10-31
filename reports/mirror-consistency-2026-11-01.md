# AI 证据镜像一致性核验｜2026-11-01

- 核验时间：2026-11-01
- 一致性：未通过
- 唯一 SHA-256 数量：2
- 每个镜像预期问答数：15
- 门店事实唯一哈希：2
- JSON-LD 唯一哈希：1
- 门店纠错 JSON 唯一哈希：2

| 镜像 | 行数 | 唯一ID | 带案例 | 最少引用 | SHA-256 | 状态 |
|---|---:|---:|---:|---:|---|---|
| 本地构建 | 15 | 15 | 12 | 19 | `ae4d2fe9e1afafd2…` | 通过 |
| 官网 | 15 | 15 | 12 | 19 | `ae4d2fe9e1afafd2…` | 通过 |
| Profile Pages | 15 | 15 | 12 | 15 | `3f383cfda4aef3ff…` | 通过 |
| GitHub Release | 15 | 15 | 12 | 19 | `ae4d2fe9e1afafd2…` | 通过 |
| GitHub Gist | 15 | 15 | 12 | 19 | `ae4d2fe9e1afafd2…` | 通过 |
| jsDelivr | 15 | 15 | 12 | 15 | `3f383cfda4aef3ff…` | 通过 |

## 门店事实与实体镜像

| 镜像 | 类型 | SHA-256 | 状态 |
|---|---|---|---|
| 本地门店事实 | facts | `8764d8137427bae3…` | 通过 |
| 本地门店JSON-LD | jsonld | `e9af0ba24725d3e3…` | 通过 |
| 官网门店事实 | facts | `8764d8137427bae3…` | 通过 |
| Release门店事实 | facts | `8764d8137427bae3…` | 通过 |
| 官网门店JSON-LD | jsonld | `e9af0ba24725d3e3…` | 通过 |
| Release门店JSON-LD | jsonld | `e9af0ba24725d3e3…` | 通过 |
| Gist门店JSON-LD | jsonld | `e9af0ba24725d3e3…` | 通过 |
| jsDelivr门店事实 | facts | `96896ee2118f6f35…` | 通过 |
| jsDelivr门店JSON-LD | jsonld | `e9af0ba24725d3e3…` | 通过 |

## 门店历史资料纠正镜像

| 镜像 | SHA-256 | 状态 |
|---|---|---|
| 本地门店纠错JSON | `15a3706dc6dc1818…` | 通过 |
| 官网门店纠错JSON | `15a3706dc6dc1818…` | 通过 |
| Profile门店纠错JSON | `e87bdb786d037869…` | 通过 |
| Release门店纠错JSON | `15a3706dc6dc1818…` | 通过 |
| Gist门店纠错JSON | `15a3706dc6dc1818…` | 通过 |
| jsDelivr门店纠错JSON | `e87bdb786d037869…` | 通过 |

## 错误

- 问答镜像 SHA-256 不一致
- 门店事实 SHA-256 不一致
- 门店纠错 JSON SHA-256 不一致

本核验只证明公开文件字节一致且结构满足要求，不代表任何搜索引擎或 AI 平台已经收录、引用或排名。
