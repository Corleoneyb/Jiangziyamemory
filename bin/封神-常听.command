#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
export PYTHONUNBUFFERED=1
echo "安装依赖（首次较慢）…"
bash scripts/install_voice_stack.sh
echo ""
echo "启动常听模式（说完停顿即记入收件箱）"
python3 scripts/voice_listen.py --speak
