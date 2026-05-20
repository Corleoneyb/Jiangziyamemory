#!/usr/bin/env python3
"""点一下说一句话：VAD → 识别 → 收件箱 → 推微信 → 关终端。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_listen import record_until_pause, speak_ack  # noqa: E402
from voice_common import append_inbox, transcribe  # noqa: E402
from voice_inbox_util import close_terminal_front_window  # noqa: E402

ONCE_KW = dict(
    end_non_speech_ms=1200,
    min_speech_ms=600,
    max_sec=180,
    vad_aggressiveness=2,
)


def notify(title: str, msg: str) -> None:
    safe = msg.replace('"', "'")[:120]
    subprocess.run(
        ["osascript", "-e", f'display notification "{safe}" with title "{title}"'],
        check=False,
    )


def main() -> int:
    code = 1
    try:
        subprocess.run(["say", "-v", "Ting-Ting", "请说"], check=False)
        print("【说一句】说完停一下即可…")
        wav = record_until_pause(**ONCE_KW)
        if wav is None:
            subprocess.run(["say", "-v", "Ting-Ting", "没听到人声"], check=False)
            notify("封神", "没听到人声")
            return 1
        print("识别中…（small 模型首次可能 20～40 秒）")
        notify("封神", "识别中")
        try:
            text = transcribe(wav)
        except Exception as e:
            subprocess.run(["say", "-v", "Ting-Ting", "识别失败"], check=False)
            print(e)
            return 1
        if not text.strip():
            subprocess.run(["say", "-v", "Ting-Ting", "没听清"], check=False)
            return 1
        print(f"【你说】{text}")
        append_inbox(text, "点按", notify=True)
        speak_ack()
        notify("封神", "已记入并推送")
        code = 0
    finally:
        close_terminal_front_window()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
