#!/usr/bin/env python3
"""按键说话 → 转文字 → inbox/立境者语音收件箱.md"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_common import INBOX_MD, VOICE_DIR, append_inbox, record_wav, transcribe  # noqa: E402

try:
    import speech_recognition as sr
except ImportError:
    raise SystemExit("请先运行: bash scripts/install_voice_stack.sh") from None


def one_session() -> bool:
    input("\n按回车开始录音…")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    wav = VOICE_DIR / f"{stamp}.wav"
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        record_wav(wav)
    except KeyboardInterrupt:
        return False
    print("识别中…")
    try:
        text = transcribe(wav)
    except sr.UnknownValueError:
        print("【未识别到文字】")
        return True
    except sr.RequestError as e:
        raise SystemExit(f"识别需联网: {e}") from e
    print(f"【识别】{text}")
    append_inbox(text, "按键说话")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    print("封神 · 语音按键（回车开始 / 回车结束）")
    print(f"收件箱：{INBOX_MD}")
    while True:
        if not one_session():
            break
        if args.once:
            break
        if input("\n继续回车，q 退出：").strip().lower() == "q":
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
