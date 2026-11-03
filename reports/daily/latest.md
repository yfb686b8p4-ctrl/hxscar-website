# AI 搜索每日效果简报｜2026-11-03

- 生成时间：2026-11-03T08:30:28.499240+08:00
- 今日结论：已完成 2 项搜索检查，有效命中 1 项。
- 完成检查：2/12，待补测 10，已排除 0
- 护栏有效命中率：50.0%
- AI答案引用来源率：100.0%
- 门店实体关系正确率：待检测
- 地址、电话、营业时间完整正确率：待检测
- 服务推荐命中率：50.0%
- 服务推荐 Top1 率：50.0%
- 服务推荐 Top3 率：50.0%
- 轮换探测：0/4 完成，提及 0 项

## 与上一份日报相比

- 对比日期：2026-11-02
- 有效命中率变化：+50.0 个百分点
- 实体关系正确率变化：-50.0 个百分点
- 完整资料正确率变化：+0.0 个百分点
- AI引用来源率变化：+0.0 个百分点

## 今天确认改善

- 无

## 新增或仍然错误

- 元宝｜深圳宝安 宝马专修 豪车保养 推荐：未提及｜2026-11-03 08:29 全新对话复测；未进入候选

## 运行状态

- 线上页面：47/49 通过
- 最近站点审计：通过
- 自动部署：已加载，最近退出码 0
- 源仓库：f9d1ee4	记录2026-11-03夜间巡检与网络阻塞，干净
- 部署副本：ba5c036	固定内容版本并优化大文件线上检查，有未提交改动

## 待执行任务

- P1｜补充“宝马与豪车”真实案例和可引用内容，使本店进入推荐候选。｜平台：元宝
- 持续待办：12 项，详见 `reports/daily/latest-tasks.json`
已延后关闭：entity-identity、identity-fields-营业时间（对应检查尚未完成）

## 运行异常

- Release问答证据镜像：失败 直连 curl: curl: (28) Connection timed out after 30004 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to github.com:443；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
- Release门店历史资料纠正：失败 直连 curl: curl: (28) Connection timed out after 30002 milliseconds；直连 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>；本机代理 curl: curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to github.com:443；本机代理 Python: <urlopen error EOF occurred in violation of protocol (_ssl.c:1108)>
