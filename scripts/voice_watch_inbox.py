#!/usr/bin/env python3
"""监视 inbox/voice/*.wav，自动识别写入收件箱。"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_common import VOICE_DIR, append_inbox, transcribe  # noqa: E402

import speech_recognition as sr  # noqa: E402

SEEN: set[str] = set()


def process_file(path: Path) -> None:
    if path.suffix.lower() != ".wav":
        return
    key = str(path.resolve())
    if key in SEEN or path.stat().st_size < 1000:
        return
    time.sleep(0.5)
    print(f"处理 {path.name}…")
    try:
        text = transcribe(path)
    except sr.UnknownValueError:
        SEEN.add(key)
        return
    except Exception as e:
        print(f"  失败: {e}")
        SEEN.add(key)
        return
    if text:
        append_inbox(text, path.name)
    SEEN.add(key)


def main() -> int:
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"监视 {VOICE_DIR} · Ctrl+C 退出")
    while True:
        for p in VOICE_DIR.glob("*.wav"):
            process_file(p)
        time.sleep(2)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已停止")
