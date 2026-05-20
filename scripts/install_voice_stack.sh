#!/usr/bin/env bash
# 安装语音通道依赖（Mac / 殿址机 Git Bash）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "【语音】安装 Python 依赖…"
python3 -m pip install --user -U pip
python3 -m pip install --user -r requirements-voice.txt

mkdir -p inbox/voice

echo ""
echo "【语音】预下载 Whisper tiny（首次约 1～3 分钟）…"
python3 -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8'); print('Whisper OK')"

echo ""
echo "【语音】麦克风：系统设置 → 隐私 → 麦克风 → 只开 Cursor（在 Cursor 里跑命令时）"
echo "【语音】试跑：python3 scripts/voice_ptt.py --once"
echo "【语音】常开：python3 scripts/voice_listen.py"
echo "【语音】朗读：python3 scripts/voice_speak.py \"你好立境者\""
