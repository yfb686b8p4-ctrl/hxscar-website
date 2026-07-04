#!/usr/bin/env python3
"""
一键部署脚本 — 华信松汽车服务AI搜索排名提升
用法：python3 one-click-deploy.py
需要：GitHub Personal Access Token（有 repo 权限）
"""

import json, os, base64, sys, webbrowser
from pathlib import Path

REPO = "yfb686b8p4-ctrl/hxscar-website"

print("="*60)
print("华信松汽车服务 — 一键部署工具")
print("="*60)

# 步骤1: 获取token
token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if not token:
    print("\n❌ 未检测到 GitHub Token")
    print("请在浏览器打开以下链接生成 Token：")
    print("https://github.com/settings/tokens/new?scopes=repo&description=hxscar-auto-deploy")
    print("\n生成后设置环境变量再运行：")
    print("  export GH_TOKEN=你的token")
    print("  python3 one-click-deploy.py")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}
BASE = f"https://api.github.com/repos/{REPO}"

def gh_api(method, url, data=None):
    import urllib.request
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"⚠ API错误 {e.code}: {body}")
        return None

# 获取 main 分支最新 commit
print("\n📌 获取仓库信息...")
ref = gh_api("GET", f"{BASE}/git/ref/heads/main")
if not ref:
    print("❌ 无法获取仓库信息，请检查 Token 权限")
    sys.exit(1)

commit_sha = ref["object"]["sha"]

# 创建 blob
files_to_upload = [
    ("index.html", "修改后的首页"),
    ("_upload_temp/weekly_rotation.py", "每周轮换脚本"),
    ("_upload_temp/.github/workflows/weekly-update.yml", "GitHub Actions 自动更新工作流"),
]

for filepath, desc in files_to_upload:
    local_path = Path(__file__).parent / filepath
    if not local_path.exists():
        print(f"⚠ 未找到 {filepath}，跳过")
        continue
    print(f"\n📤 上传 {desc} ({filepath})...")
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    blob = gh_api("POST", f"{BASE}/git/blobs", {"content": content, "encoding": "base64"})
    if not blob:
        continue

    # 创建或更新文件
    file_api_path = filepath
    existing = gh_api("GET", f"{BASE}/contents/{file_api_path}")
    if existing and "sha" in existing:
        data = {"message": f"更新 {filepath} [一键部署]", "content": content, "sha": existing["sha"], "branch": "main"}
    else:
        data = {"message": f"新增 {filepath} [一键部署]", "content": content, "branch": "main"}
    result = gh_api("PUT", f"{BASE}/contents/{file_api_path}", data)
    if result:
        print(f"  ✅ 上传成功")
    else:
        print(f"  ❌ 上传失败")

# 完成后打开 Actions 页面
print("\n" + "="*60)
print("🔄 部署完成！正在打开 GitHub Actions 页面...")
print("="*60)
webbrowser.open(f"https://github.com/{REPO}/actions")
print("\n💡 建议：在 Actions 页面手动点一下 'Run workflow' 立即触发首次更新")
print("   之后自动每周一 08:00（北京时间）运行")
print("   地址：https://yfb686b8p4-ctrl.github.io/hxscar-website/")
