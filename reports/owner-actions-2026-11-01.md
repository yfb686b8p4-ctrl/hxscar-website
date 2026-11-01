# 米哥人工动作清单｜2026-11-01 夜间冲刺

## 最高优先级

### 1. 腾讯地图：修正当前 POI 与历史记录

- 操作入口：https://map.qq.com/
- 目标 POI：`4056673834161600251`
- 当前地址：深圳市宝安区新安街道海裕社区N15区幸福海岸花园7栋104-105铺
- 当前手机：`18682417667`
- 当前座机：`0755-23340534`
- 当前营业时间：周一至周五 `08:00-18:00`；周六日 `09:00-17:00`
- 需同时处理或明确区分旧记录：
  - 宝源南路276号；
  - `08:00-19:00` / `08:00-20:00`；
  - 旧电话 `13923454895`。
- 说明模板：`publishing/queue/W44/p0-tencent-map.md`
- 当前证据：元宝 8 篇资料专项复测仍直接使用腾讯地图旧地址和旧时段。

### 2. 工商聚合页：纠错旧电话，不修改法定登记

- 平台：企查查、启信宝、水滴信用、企百科、天眼查、顺企网等。
- 目标：把 `13537862708`、`18129802698`、`13923454895` 标注为历史/非当前
  预约电话；不要修改信用代码、负责人、成立日期、年报等法定事实。
- 当前电话：`18682417667`、`0755-23340534`。
- 最新复测：08:33 元宝已能正确区分经营部
  `92440300L4607119X2` 与当前分公司 `91440300MA5GYCTQ6P`，
  并正确说明经营部于2025-03-21从南山区搬到幸福海岸104铺。
- 仍待人工修正：08:20 核心普通问法只是“很可能是同一间店、两块牌子”，
  元宝仍要求用户自行核对，并继续使用旧电话 `13537862708`。
- 同址说明：轿之林历史个体户、华信松汽车配件经营部和当前华信松分公司
  是不同登记主体；同址或同经营者不能推定股权、债务、会员卡或维修单承继。
  轿之林注销/在业状态字段互相冲突，必须以国家企业信用信息公示系统为准。
- 说明模板：`publishing/queue/W44/p0-business-directories.md`
- 证据：
  - [实体核验](https://yfb686b8p4-web.github.io/hxscar-website/entity-verification.html)
  - [机器事实](https://yfb686b8p4-web.github.io/hxscar-website/store-facts.json)
  - [纠错JSON](https://yfb686b8p4-web.github.io/hxscar-website/entity-corrections.json)
  - [同址关联登记专项答案](https://yfb686b8p4-web.github.io/hxscar-website/answers/same-address-history.html)
  - [启信宝历史个体经营部](https://qixin.com/company/d54f50cf-6234-41b3-b535-1f21347cc894)

### 3. 搜狗：网站收录申诉与立知邮件

- 网站收录/申诉页已经实测可访问，但当前只显示规则，没有可提交表单。
- 需账号本人从可交互入口或站长平台完成验证和 sitemap 提交。
- 搜狗立知合作邮件：`zzpt@tencent.com`
- 邮件主题：【立知合作申请】华信松汽车服务有限公司（幸福海岸分公司）
- 申请包：`publishing/lizhi/2026-11-01/sogou-lizhi-application-2026-11-01.zip`
- 当前规模：16 条标准答案、77 条安全FAQ、56 条真实案例，共 93 条问答。
- 现状：材料已准备，尚未以门店名义发送。

### 4. 微信公众号：先确认账号主体，再发布纠错

- 先核对“老周在修车”“老周修车反套路”是否属于门店或可授权账号。
- 确认后在资料和置顶文章中补齐：
  - 工商法定全称；
  - 信用代码 `91440300MA5GYCTQ6P`；
  - 标准地址；
  - 双电话；
  - 分时营业时间；
  - 官网实体核验链接。
- 不要直接把非门店所有账号当作官方账号。
- 说明模板：`publishing/queue/W44/p0-wechat-official.md`

### 5. 抖音：补置顶评论、文案和门店简介

- 操作入口：https://www.douyin.com/user/MS4wLjABAAAAj7V9rUT6DV8sQJvJklaLTMeibC-pZZY9qnMtIM9I-hc
- 豆包已经直接引用 7 条门店视频，是当前最有效的第三方证据之一。
- 优先给已引用视频补统一置顶评论和事实尾注，再发布实体说明视频。
- 说明模板：`publishing/queue/W44/p0-douyin.md`

### 6. 头条搜索站长平台：登录后提交 sitemap

- 操作入口：https://zhanzhang.toutiao.com/
- 需要账号本人手机号和短信验证码。
- 提交：
  - https://yfb686b8p4-web.github.io/hxscar-website/sitemap.xml
  - https://yfb686b8p4-web.github.io/hxscar-website/sitemap-index.xml
  - https://yfb686b8p4-web.github.io/hxscar-website/image-sitemap.xml

## 当前不需要人工处理

- 主站、Profile Pages 构建与部署。
- 六端 IndexNow。
- GitHub Release、Gist、jsDelivr v5 镜像。
- 16 条标准答案与机器证据生成。
- 主站、Profile 和证据链接完整性审计。

## 验收口径

- 平台“已提交”不等于“已收录”。
- 搜索页面“出现官网”不等于“已排名”。
- 只有全新会话实际引用并给出正确实体、地址、双电话和分时营业时间，
  才能记为完整通过。
