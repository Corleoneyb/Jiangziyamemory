#!/usr/bin/env python3
"""常听 / 点按：用语音活动检测（VAD）判断「你说完了」，不靠环境安静。"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_common import INBOX_MD, VOICE_DIR, append_inbox, transcribe  # noqa: E402

SAMPLERATE = 16000
FRAME_MS = 30  # webrtcvad 仅支持 10/20/30 ms


def speak_ack() -> None:
    subprocess.run(["say", "-v", "Ting-Ting", "已记下"], check=False)


def speak_quick_received() -> None:
    """收音刚结束、转写尚未完成时先播，避免弘尊干等十几秒以为死机。"""
    subprocess.run(["say", "-v", "Ting-Ting", "收到"], check=False)


def save_wav(path: Path, audio_int16, samplerate: int = SAMPLERATE) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_int16.tobytes())


def record_until_pause(
    *,
    end_non_speech_ms: int = 1200,
    min_speech_ms: int = 600,
    max_sec: float = 180,
    vad_aggressiveness: int = 2,
) -> Path | None:
    """结束条件：人声 VAD 判定你已停说（约 1.2 秒无语音），不是环境安静。

    空调、鸟叫等持续噪音不应单独触发结束；只有「检测不到人声」才结束。
    """
    import numpy as np
    import sounddevice as sd
    import webrtcvad

    frame_len = int(SAMPLERATE * FRAME_MS / 1000)
    vad = webrtcvad.Vad(vad_aggressiveness)

    print(
        f"…听（对着 Mac 说，说完停约 {end_non_speech_ms/1000:.1f} 秒即可；"
        f"空调鸟叫可忽略，最长 {int(max_sec)} 秒）"
    )

    chunks: list = []
    in_speech = False
    speech_ms = 0
    non_speech_ms = 0
    t0 = time.time()

    with sd.InputStream(
        samplerate=SAMPLERATE,
        channels=1,
        dtype="int16",
        blocksize=frame_len,
    ) as stream:
        while time.time() - t0 < max_sec:
            data, _ = stream.read(frame_len)
            if data is None or len(data) == 0:
                continue
            pcm = data.tobytes()
            try:
                is_speech = vad.is_speech(pcm, SAMPLERATE)
            except Exception:
                is_speech = False

            if not in_speech:
                if is_speech:
                    in_speech = True
                    chunks.append(data.copy())
                    speech_ms = FRAME_MS
                    non_speech_ms = 0
                continue

            chunks.append(data.copy())
            if is_speech:
                speech_ms += FRAME_MS
                non_speech_ms = 0
            else:
                non_speech_ms += FRAME_MS
                if speech_ms >= min_speech_ms and non_speech_ms >= end_non_speech_ms:
                    break

    if not chunks:
        return None

    audio = np.concatenate(chunks, axis=0).flatten()
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = VOICE_DIR / f"{stamp}.wav"
    save_wav(path, audio)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--speak", action="store_true")
    args = parser.parse_args()

    print("【常听】直接说话，停说后记入。Ctrl+C 退出。")
    print(f"收件箱：{INBOX_MD}\n")

    while True:
        try:
            wav = record_until_pause()
        except KeyboardInterrupt:
            print("\n已退出")
            break
        if wav is None:
            print("（未检测到人声，请再试）\n")
            continue
        print("已收音，正在转写…（本机 Whisper，长句可能要十几秒）", flush=True)
        if args.speak:
            speak_quick_received()
        try:
            text = transcribe(wav)
        except Exception as e:
            print(f"识别失败: {e}\n")
            continue
        if not text.strip():
            print("（未听清）\n")
            continue
        print(f"【你说】{text}")
        append_inbox(text, "常听")
        if args.speak:
            speak_ack()
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
