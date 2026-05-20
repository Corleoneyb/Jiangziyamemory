#!/usr/bin/env python3
"""朗读文字（Mac say / Windows 可扩展）。

用法:
  python3 scripts/voice_speak.py "姜子牙，封神榜何在"
  python3 scripts/voice_speak.py --last   # 读收件箱最后一条
"""

from __future__ import annotations

import argparse
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX_MD = ROOT / "inbox" / "弘尊语音收件箱.md"
LEGACY_INBOX = ROOT / "inbox" / "立境者语音收件箱.md"


def last_inbox_line() -> str:
    path = INBOX_MD if INBOX_MD.exists() else LEGACY_INBOX
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n## \d{4}-\d{2}-\d{2}", text)
    if len(blocks) < 2:
        return text.strip()
    last = blocks[-1].split("\n", 1)[-1].strip()
    return last[:500]


def say(text: str) -> None:
    text = text.strip()
    if not text:
        print("无内容可读")
        return
    if platform.system() == "Darwin":
        subprocess.run(["say", "-v", "Ting-Ting", text], check=False)
    elif platform.system() == "Windows":
        # PowerShell SAPI
        ps = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Speak('{text.replace(chr(39), chr(39)+chr(39))}')"
        )
        subprocess.run(["powershell", "-Command", ps], check=False)
    else:
        print(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="")
    parser.add_argument("--last", action="store_true")
    args = parser.parse_args()
    t = last_inbox_line() if args.last else args.text
    say(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
