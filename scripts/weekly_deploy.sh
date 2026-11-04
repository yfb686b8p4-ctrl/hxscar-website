#!/bin/bash
# 每周生成内容并推送到独立 GitHub Pages 仓库。

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export GITHUB_REPOSITORY="yfb686b8p4-web/hxscar-website"
export SITE_URL="https://yfb686b8p4-web.github.io/hxscar-website/"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

log() {
  printf '[%s] %s\n' "$(TZ='Asia/Shanghai' date '+%F %T')" "$*"
}

fail() {
  log "错误：$*" >&2
  exit 1
}

remote_name=web
if ! git remote get-url "$remote_name" >/dev/null 2>&1; then
  remote_name=origin
fi

if [ -n "$(git status --porcelain)" ]; then
  fail "部署副本存在未提交改动，请先人工核对，本次不生成也不推送。"
fi

log "同步 ${remote_name}/main，确认部署副本没有落后或分叉。"
git fetch "$remote_name" main --prune
remote_head="$(git rev-parse FETCH_HEAD)"
local_head="$(git rev-parse HEAD)"

if [ "$remote_head" != "$local_head" ]; then
  if git merge-base --is-ancestor "$remote_head" HEAD; then
    log "部署副本本地提交领先远端，继续使用本地提交。"
  elif git merge-base --is-ancestor HEAD "$remote_head"; then
    log "部署副本落后远端，先快进到最新线上版本。"
    git merge --ff-only FETCH_HEAD
  else
    fail "部署副本与远端 main 已分叉，拒绝自动更新。"
  fi
fi

week="$(TZ='Asia/Shanghai' date '+%V')"

python3 weekly_rotation.py
python3 multi_platform_publisher.py
python3 scripts/content_matrix_builder.py
python3 scripts/rank_monitor.py --init
python3 scripts/visibility_insights.py
python3 scripts/authority_queue.py --week "$week"
python3 scripts/site_builder.py
python3 scripts/site_audit.py

git add index.html answers.html faq.html cases.html store-profile.html entity-verification.html store-facts.json store-facts.jsonld entity-corrections.json case-evidence.json qa-evidence.jsonl douyin-video-evidence.json feed.xml robots.txt sitemap.xml sitemap-index.xml image-sitemap.xml llms.txt llms-full.txt
git add answers
git add aliases
git add cases evidence-policy.html
git add services models
git add assets
git add downloads
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

submit_indexes() {
  python3 scripts/submit_indexnow.py --wait \
    || log "主站 IndexNow 提交失败，等待下次部署重试。"
  python3 scripts/submit_profile_indexnow.py --wait \
    || log "Profile IndexNow 提交失败，等待下次部署重试。"
}

proxy_ok=false
if curl -sS --max-time 3 --proxy http://127.0.0.1:7897 \
  https://api.github.com/rate_limit >/dev/null 2>&1; then
  proxy_ok=true
fi

if [ "$proxy_ok" = true ]; then
  if git -c http.proxy=http://127.0.0.1:7897 \
    -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1 -c http.lowSpeedTime=15 \
    push "$remote_name" HEAD:main; then
    log "已通过代理推送。"
    pushed_head="$(git rev-parse HEAD)"
    published_head="$(git ls-remote "$remote_name" refs/heads/main | awk '{print $1}')"
    [ "$published_head" = "$pushed_head" ] \
      || fail "推送后线上 main 与本地 HEAD 不一致。"
    submit_indexes
    exit 0
  fi
  log "代理推送失败，改用直连重试。"
fi

git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1 -c http.lowSpeedTime=15 \
  push "$remote_name" HEAD:main
log "已通过直连推送。"
pushed_head="$(git rev-parse HEAD)"
published_head="$(git ls-remote "$remote_name" refs/heads/main | awk '{print $1}')"
[ "$published_head" = "$pushed_head" ] \
  || fail "推送后线上 main 与本地 HEAD 不一致。"
submit_indexes
