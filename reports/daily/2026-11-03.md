# AI 搜索每日效果简报｜2026-11-03

- 生成时间：2026-11-03T03:21:59.058602+08:00
- 今日结论：基础状态检查完成，搜索结果尚未实测。
- 完成检查：0/12，待补测 12，已排除 0
- 护栏有效命中率：待检测
- AI答案引用来源率：待检测
- 门店实体关系正确率：待检测
- 地址、电话、营业时间完整正确率：待检测
- 服务推荐命中率：待检测
- 服务推荐 Top1 率：待检测
- 服务推荐 Top3 率：待检测
- 轮换探测：0/4 完成，提及 0 项

## 与上一份日报相比

- 对比日期：2026-11-02；今天尚无已完成的护栏结果，暂不计算升降幅。

## 今天确认改善

- 无

## 新增或仍然错误

- 无

## 运行状态

- 线上页面：35/49 通过
- 最近站点审计：通过
- 自动部署：已加载，最近退出码 0
- 源仓库：f363a7e	同步GitHub API发布提交，干净
- 部署副本：ba5c036	固定内容版本并优化大文件线上检查，有未提交改动

## 待执行任务

- 持续待办：12 项，详见 `reports/daily/latest-tasks.json`
已延后关闭：entity-identity、identity-fields-营业时间（对应检查尚未完成）

## 运行异常

- 搜索问答：失败 直连 curl: curl: (28) Operation timed out after 963784 milliseconds with 98304 out of 131072 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 409168 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- 问答证据JSONL：失败 直连 curl: curl: (28) Operation timed out after 962778 milliseconds with 0 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 410164 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- 标准问答RSS：失败 直连 curl: curl: (28) Operation timed out after 962739 milliseconds with 0 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 410177 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- 门店品牌图：失败 直连 curl: curl: (28) Connection timed out after 962452 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 410165 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- 门店外观图：失败 直连 curl: curl: (28) Connection timed out after 962407 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 410189 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- 门店响应式外观图：失败 直连 curl: curl: (28) Operation timed out after 962284 milliseconds with 0 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to yfb686b8p4-web.github.io:443；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- Release问答证据镜像：失败 直连 curl: curl: (28) Operation timed out after 1031059 milliseconds with 39810 out of 78413 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 737002 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- Gist问答证据镜像：失败 直连 curl: curl: (28) Operation timed out after 1031173 milliseconds with 32768 out of 78413 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 738010 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- Release门店事实Markdown：失败 直连 curl: curl: (28) Connection timed out after 1030287 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 737057 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- jsDelivr门店事实：失败 直连 curl: curl: (28) Operation timed out after 1030613 milliseconds with 20744 bytes received；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 737054 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- jsDelivr门店JSON-LD：失败 直连 curl: curl: (28) Connection timed out after 1030111 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 738006 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- jsDelivr门店历史资料纠正：失败 直连 curl: curl: (28) Connection timed out after 1029357 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (28) Connection timed out after 738015 milliseconds；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- jsDelivr问答证据镜像：失败 直连 curl: curl: (6) Could not resolve host: cdn.jsdelivr.net；直连 Python: <urlopen error [Errno 8] nodename nor servname provided, or not known>；本机代理 curl: curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to cdn.jsdelivr.net:443；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- Profile IndexNow验证：失败 直连 curl: curl: (6) Could not resolve host: yfb686b8p4-web.github.io；直连 Python: <urlopen error [Errno 8] nodename nor servname provided, or not known>；本机代理 curl: curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to yfb686b8p4-web.github.io:443；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
