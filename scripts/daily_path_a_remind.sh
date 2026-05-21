#!/usr/bin/env bash
# 路径 A · 每日一次提醒：即刻有互动再露脸回，不要求报数。
# cron 示例（弘尊本机，每天 10:00）：
#   0 10 * * * cd ~/Jiangziya/Jiangziyamemory && ./scripts/daily_path_a_remind.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MSG="【封神】路径A：打开即刻看评论/私信即可，有再回；不必报数。无互动可跳过。"
python3 scripts/fengshen_remind.py --message "$MSG" --audit 2>/dev/null || echo "$MSG"
