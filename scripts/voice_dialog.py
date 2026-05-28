#!/usr/bin/env python3
"""半双工语音对话：说完 → 脑 → Mac say 答复（真姜子牙 Z2 · L1）。

用法:
  python3 scripts/voice_dialog.py          # 循环，回车开始一轮
  python3 scripts/voice_dialog.py --once

环境:
  WHISPER_MODEL=base|small
  OLLAMA_HOST=http://<殿址机IP>:11434  OLLAMA_MODEL=qwen2.5:7b   # 主脑，见 docs/殿址机-姜子牙脑-v1.md
  OPENAI_API_KEY=...  # 仅 OLLAMA 不可用时的备用，非默认
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_common import append_inbox, transcribe  # noqa: E402
from voice_dialog_brain import brain_reply, load_dotenv, write_last_reply  # noqa: E402
from voice_listen import record_until_pause  # noqa: E402

VOICE_DIR = ROOT / "inbox" / "voice"


def say_mac(text: str) -> None:
    text = text.replace('"', " ").replace("\n", "，")
    if not text:
        return
    parts = re.split(r"(?<=[。！？；])", text)
    parts = [p.strip() for p in parts if p.strip()] or [text]
    for i, p in enumerate(parts[:4]):
        subprocess.run(["say", "-v", "Ting-Ting", p], check=False)
        if i == 0 and len(parts) > 1:
            print(f"【先播】{p}")


def one_round() -> bool:
    import datetime as dt

    input("\n【对话】按回车开始说…")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    wav = VOICE_DIR / f"dialog-{stamp}.wav"
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        recorded = record_until_pause(
            end_non_speech_ms=1000,
            min_speech_ms=500,
            max_sec=90,
            vad_aggressiveness=2,
        )
    except KeyboardInterrupt:
        return False
    if recorded is None:
        say_mac("没听到人声。")
        return True
    wav = recorded
    subprocess.run(["say", "-v", "Ting-Ting", "收到"], check=False)
    print("识别中…")
    user = transcribe(wav)
    if not user:
        say_mac("没听清，再说一遍。")
        return True
    print(f"【弘尊】{user}")
    append_inbox(user, "语音对话", notify=False)
    print("想一句…")
    reply = brain_reply(user)
    print(f"【姜子牙】{reply}")
    write_last_reply(user, reply)
    say_mac(reply)
    return True


def main() -> int:
    import os

    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    print("真姜子牙 · 语音对话（半双工 L1）· Mac 系统音")
    host = os.environ.get("OLLAMA_HOST", "未设")
    print(f"主脑：殿址机 Ollama ({host}) · 见 docs/殿址机-姜子牙脑-v1.md")
    print("软件脸同步：avatar/last_reply.json（网页轮询或 API）")
    while True:
        if not one_round():
            break
        if args.once:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
