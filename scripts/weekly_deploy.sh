#!/bin/bash
# 每周生成内容并推送到独立 GitHub Pages 仓库。

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export GITHUB_REPOSITORY="yfb686b8p4-web/hxscar-website"
export SITE_URL="https://yfb686b8p4-web.github.io/hxscar-website/"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

python3 weekly_rotation.py
python3 scripts/site_builder.py
python3 multi_platform_publisher.py
python3 scripts/site_audit.py

week="$(TZ='Asia/Shanghai' date '+%V')"
git add index.html faq.html cases.html robots.txt sitemap.xml llms.txt
git add reports/site-audit.json reports/site-audit.md
if [ -d "platform_content/W${week}" ]; then
  git add -f "platform_content/W${week}"
fi

if git diff --cached --quiet; then
  echo "没有内容变化，无需提交"
  exit 0
fi

git commit -m "每周内容更新 W${week} · $(TZ='Asia/Shanghai' date '+%Y-%m-%d')"

git_proxy=()
if curl -sS --max-time 2 --proxy http://127.0.0.1:7897 \
  https://api.github.com/rate_limit >/dev/null 2>&1; then
  git_proxy=(-c http.proxy=http://127.0.0.1:7897)
fi

remote_name=web
if ! git remote get-url "$remote_name" >/dev/null 2>&1; then
  remote_name=origin
fi

git "${git_proxy[@]}" -c http.version=HTTP/1.1 push "$remote_name" HEAD:main
