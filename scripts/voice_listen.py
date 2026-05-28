#!/usr/bin/env python3
"""常听 / 点按：用语音活动检测（VAD）判断「你说完了」，不靠环境安静。"""

from __future__ import annotations

import argparse
import datetime as dt
import queue
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


def _frame_level_mean(data) -> float:
    import numpy as np

    return float(np.abs(data.astype(np.float64)).mean())


def record_until_pause(
    *,
    end_non_speech_ms: int = 1200,
    min_speech_ms: int = 1200,
    max_sec: float = 180,
    vad_aggressiveness: int = 3,
    peak_min: float = 120.0,
) -> Path | None:
    """结束条件：人声 VAD + 能量门槛，减少风扇/空调误起录。

    说明：本机 **没有「只认你声纹」**；要「按住再录」用 `voice_ptt.py`。
    """
    import numpy as np
    import sounddevice as sd
    try:
        import webrtcvad  # type: ignore
    except Exception:
        webrtcvad = None

    frame_len = int(SAMPLERATE * FRAME_MS / 1000)
    vad = webrtcvad.Vad(vad_aggressiveness) if webrtcvad else None
    if vad is None:
        print("（未安装 webrtcvad，改用能量阈值模式）")

    print(
        f"…听（对着 Mac 说，说完停约 {end_non_speech_ms/1000:.1f} 秒；"
        f"至少约 {min_speech_ms/1000:.1f} 秒人声才落盘；最长 {int(max_sec)} 秒）"
    )

    chunks: list = []
    in_speech = False
    speech_ms = 0
    non_speech_ms = 0
    t0 = time.time()

    q: queue.Queue = queue.Queue()

    def _on_audio(indata, _frames, _time_info, _status) -> None:
        q.put(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLERATE,
        channels=1,
        dtype="int16",
        blocksize=frame_len,
        callback=_on_audio,
    ):
        while time.time() - t0 < max_sec:
            try:
                data = q.get(timeout=1.0)
            except queue.Empty:
                continue
            if data is None or len(data) == 0:
                continue
            pcm = data.tobytes()
            level = _frame_level_mean(data)
            if vad is None:
                is_speech = level >= peak_min
            else:
                try:
                    is_speech = vad.is_speech(pcm, SAMPLERATE)
                except Exception:
                    is_speech = False

            if not in_speech:
                # 起录：VAD 认为像语音 **且** 本帧能量够高，避免纯环境底噪起录
                if is_speech and level >= peak_min:
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
    parser.add_argument("--vad", type=int, default=3, choices=[0, 1, 2, 3], help="webrtcvad 激进程度，越大越不易把噪音当人声")
    parser.add_argument(
        "--min-speech-ms",
        type=int,
        default=1200,
        help="至少多长「像说话」才允许停说落盘，防短促噪音",
    )
    parser.add_argument(
        "--peak-min",
        type=float,
        default=120.0,
        help="起录帧平均绝对幅值下限（int16）；环境仍误触可调高，如 200",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=2.0,
        help="成功写入收件箱后暂停监听秒数，防连环误触",
    )
    args = parser.parse_args()

    print("【常听】直接说话，停说后记入。Ctrl+C 退出。")
    print("【说明】常听≠只认你声音；要按住再录用：python3 scripts/voice_ptt.py")
    print(f"收件箱：{INBOX_MD}\n")

    while True:
        try:
            wav = record_until_pause(
                vad_aggressiveness=args.vad,
                min_speech_ms=args.min_speech_ms,
                peak_min=args.peak_min,
            )
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
        if args.cooldown > 0:
            time.sleep(args.cooldown)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
