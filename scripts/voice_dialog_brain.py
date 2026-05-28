"""姜子牙语音脑：转写后的答复逻辑（voice_dialog / API / bridge 共用）。"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "scripts" / "jiangziya_brain_prompt.txt"
LAST_REPLY_PATH = ROOT / "avatar" / "last_reply.json"
MEMORY_DAYS = 2


def load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.is_file():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def recent_memory() -> str:
    from datetime import datetime, timedelta

    parts: list[str] = []
    for i in range(MEMORY_DAYS + 1):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = ROOT / "memories" / f"{day}.md"
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            parts.append(text[-2500:] if len(text) > 2500 else text)
    return "\n---\n".join(parts)[:6000]


def system_prompt() -> str:
    base = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.is_file() else "你是姜子牙。"
    mem = recent_memory()
    if mem:
        base += f"\n\n【近日卷宗摘要】\n{mem}"
    return base


def call_ollama(user: str) -> str | None:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
    payload = {
        "model": model,
        "prompt": f"{system_prompt()}\n\n弘尊说：{user}\n\n姜子牙答（80字以内）：",
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        return (data.get("response") or "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"【Ollama 不可用】{e}")
        return None


def call_openai(user: str) -> str | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("OPENAI_BASE", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": user},
        ],
        "max_tokens": 200,
    }
    try:
        req = urllib.request.Request(
            f"{base}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
        print(f"【API 不可用】{e}")
        return None


def fallback_reply(user: str) -> str:
    if re.search(r"听音|听榜", user):
        return "好，卷宗我记下了。你回 Cursor 跟姜子牙说一声听音，我接着派活。"
    if re.search(r"推|灵台|门", user):
        return "行，灵台推送的事你在对话里吩咐姜子牙，我这边记下了。"
    if re.search(r"臂|机械|机器人", user):
        return "机械臂选型在 deliverables 鲁班 桌面机械臂选型，你先定买不买 myCobot。"
    return f"听见了。你是说：{user[:40]}。要我做哪一件，再说具体一点。"


def brain_reply(user: str) -> str:
    reply = call_ollama(user) or call_openai(user)
    if not reply:
        reply = fallback_reply(user)
    reply = re.sub(r"\s+", " ", reply).strip()
    if len(reply) > 280:
        reply = reply[:277] + "…"
    return reply


def write_last_reply(text: str, reply: str) -> None:
    import time

    LAST_REPLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": int(time.time() * 1000),
        "text": text.strip(),
        "reply": reply.strip(),
    }
    LAST_REPLY_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
