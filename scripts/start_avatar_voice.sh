#!/usr/bin/env bash
# 一条命令：语音 API + 静态页 + 打开软件脸
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT_HTTP="${1:-8765}"
PORT_API="${2:-8766}"
cd "$ROOT"

cleanup() {
  kill "$API_PID" "$HTTP_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

python3 scripts/voice_dialog_api.py --port "$PORT_API" &
API_PID=$!
python3 -m http.server "$PORT_HTTP" &
HTTP_PID=$!
sleep 0.6
echo ""
echo "软件脸对话已就绪"
echo "  网页: http://127.0.0.1:${PORT_HTTP}/avatar/index.html"
echo "  API:  http://127.0.0.1:${PORT_API}/api/dialog"
open "http://127.0.0.1:${PORT_HTTP}/avatar/index.html" 2>/dev/null || true
wait
