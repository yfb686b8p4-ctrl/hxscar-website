# 门店落地页部署指南（免费方案 — GitHub Pages）

## 第一步：注册 GitHub 账号
1. 打开 https://github.com
2. 注册账号（免费），用户名建议用 `hxscar` 或门店相关
3. 验证邮箱

## 第二步：创建仓库
1. 点右上角「+」→「New repository」
2. Repository name 填：`hxscar`
3. 选「Public」
4. 勾选「Add a README file」
5. 点「Create repository」

## 第三步：上传落地页
1. 进入刚创建的仓库
2. 点「Add file」→「Upload files」
3. 把 `templates/shop-hxscar.html` 拖上去
4. 文件名改成 `index.html`（关键！这样访问时直接显示）
5. 点「Commit changes」

## 第四步：开启 GitHub Pages
1. 进入仓库 → Settings → Pages
2. Source 选「Deploy from a branch」
3. Branch 选「main」+ 文件夹「/(root)」
4. 点「Save」
5. 等 2 分钟，你的网址就是：`https://你的用户名.github.io/hxscar/`

## 第五步：提交百度收录
1. 打开 https://ziyuan.baidu.com
2. 注册/登录百度搜索资源平台
3. 添加站点：输入你的 GitHub Pages 网址
4. 验证所有权：选 CNAME 验证，按提示操作
5. 提交落地页链接让百度抓取

## 第六步：把网址填到地图平台
- 百度商户中心 → 门店信息 → 官网地址
- 高德商户中心 → 门店信息 → 官网地址
- 这样地图上搜到你门店时也能看到官网链接
