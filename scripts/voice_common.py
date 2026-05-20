"""语音通道：识别结果一律以简体中文交给弘尊。"""

from __future__ import annotations

import os
import tempfile
import wave
from pathlib import Path

from voice_inbox_util import (
    WHISPER_PROMPT,
    finalize_for_hongzun,
    is_mostly_english,
    mark_pending,
    push_wechat,
)

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"
VOICE_DIR = INBOX / "voice"
INBOX_MD = INBOX / "弘尊语音收件箱.md"

_WHISPER_MODEL = None
MODEL_NAME = os.environ.get("WHISPER_MODEL", "small")


def append_inbox(text: str, source: str = "voice", *, notify: bool = True) -> str:
    text = finalize_for_hongzun(text)
    INBOX.mkdir(parents=True, exist_ok=True)
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = f"\n\n## {stamp} · {source}\n\n{text.strip()}\n"
    if INBOX_MD.exists():
        INBOX_MD.write_text(INBOX_MD.read_text(encoding="utf-8") + block, encoding="utf-8")
    else:
        INBOX_MD.write_text("# 弘尊语音收件箱\n" + block, encoding="utf-8")
    print(f"\n【已写入】{INBOX_MD}")
    mark_pending(text, source)
    if notify:
        if push_wechat(text):
            print("【已推微信】")
        else:
            print("【微信未推】检查 .env PushPlus")
    return text


def _whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        from faster_whisper import WhisperModel

        print(f"【语音】加载 Whisper {MODEL_NAME}（仅简体中文）…")
        _WHISPER_MODEL = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    return _WHISPER_MODEL


def transcribe_local(wav_path: Path) -> str:
    model = _whisper_model()
    segments, _ = model.transcribe(
        str(wav_path),
        language="zh",
        task="transcribe",
        initial_prompt=WHISPER_PROMPT,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return "".join(s.text for s in segments).strip()


def transcribe_google(wav_path: Path) -> str:
    import speech_recognition as sr

    r = sr.Recognizer()
    with sr.AudioFile(str(wav_path)) as source:
        audio = r.record(source)
    return r.recognize_google(audio, language="zh-CN").strip()


def transcribe(wav_path: Path) -> str:
    """本地 Whisper（zh）→ 若像英文则联网 zh-CN 重试 → 一律简体中文。"""
    text = ""
    try:
        text = transcribe_local(wav_path)
        if text and not is_mostly_english(text):
            print("【识别·本地·中文】")
            return finalize_for_hongzun(text)
    except Exception as e:
        print(f"【本地识别跳过】{e}")

    print("【识别·联网·中文】")
    try:
        text = transcribe_google(wav_path)
    except Exception as e:
        raise RuntimeError(f"中文识别失败: {e}") from e
    return finalize_for_hongzun(text)


def transcribe_audio_data(audio) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)
    path.write_bytes(audio.get_wav_data())
    try:
        return transcribe(path)
    finally:
        path.unlink(missing_ok=True)
