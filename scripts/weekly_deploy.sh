#!/bin/bash
# 每周生成内容并推送到独立 GitHub Pages 仓库。

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export GITHUB_REPOSITORY="yfb686b8p4-web/hxscar-website"
export SITE_URL="https://yfb686b8p4-web.github.io/hxscar-website/"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

week="$(TZ='Asia/Shanghai' date '+%V')"

python3 weekly_rotation.py
python3 multi_platform_publisher.py
python3 scripts/content_matrix_builder.py
python3 scripts/rank_monitor.py --init
python3 scripts/visibility_insights.py
python3 scripts/authority_queue.py --week "$week"
python3 scripts/site_builder.py
python3 scripts/site_audit.py

git add index.html answers.html faq.html cases.html store-profile.html store-facts.json robots.txt sitemap.xml llms.txt
git add services models
git add reports/site-audit.json reports/site-audit.md reports/rank-history
git add reports/daily
git add reports/recheck-*.md
git add reports/visibility-insights.json reports/visibility-insights.md
git add publishing
if [ -d "platform_content/W${week}" ]; then
  git add -f "platform_content/W${week}"
fi

if ! git diff --cached --quiet; then
  git commit -m "每周内容更新 W${week} · $(TZ='Asia/Shanghai' date '+%Y-%m-%d')"
else
  echo "没有内容变化，检查远程是否需要补推"
fi

remote_name=web
if ! git remote get-url "$remote_name" >/dev/null 2>&1; then
  remote_name=origin
fi

proxy_ok=false
if curl -sS --max-time 3 --proxy http://127.0.0.1:7897 \
  https://api.github.com/rate_limit >/dev/null 2>&1; then
  proxy_ok=true
fi

if [ "$proxy_ok" = true ]; then
  if git -c http.proxy=http://127.0.0.1:7897 \
    -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1 -c http.lowSpeedTime=15 \
    push "$remote_name" HEAD:main; then
    echo "已通过代理推送"
    python3 scripts/submit_indexnow.py --wait || echo "IndexNow 提交失败，等待下次部署重试"
    exit 0
  fi
  echo "代理推送失败，改用直连重试"
fi

git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1 -c http.lowSpeedTime=15 \
  push "$remote_name" HEAD:main
echo "已通过直连推送"
python3 scripts/submit_indexnow.py --wait || echo "IndexNow 提交失败，等待下次部署重试"

python3 scripts/submit_indexnow.py
