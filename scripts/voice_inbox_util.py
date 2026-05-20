"""语音收件箱：待处理标记、推送、简体中文强制、简易纠错。"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PENDING = ROOT / "inbox" / "voice_pending.json"
INBOX_MD = ROOT / "inbox" / "弘尊语音收件箱.md"

# 强制：口述转写为简体中文，禁止翻译成英语
WHISPER_PROMPT = (
    "以下是弘尊闫滨用普通话口述的内容。"
    "请仅用简体中文汉字逐字转写，不要翻译成英语，不要输出繁体字。"
    "封神，姜子牙，赵公明，范蠡，闻仲，比干，吴道子，门第二版文案，"
    "批阅灵台，盈利表，听音，殿址机，鲁班，硬件。"
)

REPLACEMENTS: list[tuple[str, str]] = [
    (r"門為二|门为二", "门第二版"),
    (r"照公民範理|赵公民范蠡|招公明范蠡", "赵公明范蠡"),
    (r"贏力表|赢力表", "盈利表"),
    (r"聽受見相|听受见相", "听音"),
    (r"這樣子壓", "这样子呀"),
]


def to_simplified_chinese(text: str) -> str:
    """繁体→简体；无库则原样。"""
    try:
        import zhconv

        return zhconv.convert(text, "zh-cn")
    except ImportError:
        return text


def latin_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    latin = sum(1 for c in letters if ord(c) < 128)
    return latin / len(letters)


def is_mostly_english(text: str) -> bool:
    """整段以英文字母为主则视为误识别。"""
    t = text.strip()
    if len(t) < 4:
        return False
    return latin_ratio(t) > 0.55


def refine_text(text: str) -> str:
    """弘尊可见文字：一律简体中文 + 领域纠错。"""
    t = text.strip()
    t = to_simplified_chinese(t)
    for pat, rep in REPLACEMENTS:
        t = re.sub(pat, rep, t)
    return t


def finalize_for_hongzun(text: str) -> str:
    """写入收件箱 / 推微信前的最终文本。"""
    t = refine_text(text)
    if is_mostly_english(t):
        print("【警告】识别结果像英文，请重说或改用中文短句。")
    return t


def mark_pending(text: str, source: str = "点按") -> None:
    PENDING.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "text": text,
        "source": source,
        "processed": False,
    }
    PENDING.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_pending() -> dict | None:
    if not PENDING.is_file():
        return None
    try:
        data = json.loads(PENDING.read_text(encoding="utf-8"))
        if data.get("processed"):
            return None
        return data
    except json.JSONDecodeError:
        return None


def mark_processed() -> None:
    data = load_pending()
    if not data:
        return
    data["processed"] = True
    PENDING.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def push_wechat(text: str) -> bool:
    text = finalize_for_hongzun(text)
    preview = text[:200] + ("…" if len(text) > 200 else "")
    msg = (
        "【弘尊语音·已记入】\n\n"
        f"{preview}\n\n"
        "已写入灵台。对姜子牙说：听音"
    )
    script = ROOT / "scripts" / "fengshen_remind.py"
    r = subprocess.run(
        [sys.executable, str(script), "--message", msg, "--title", "封神·语音"],
        cwd=str(ROOT),
    )
    return r.returncode == 0


def close_terminal_front_window() -> None:
    # saving no：关窗不弹「是否终止运行中进程」
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "Terminal" to if (count of windows) > 0 then close front window saving no',
        ],
        check=False,
    )
