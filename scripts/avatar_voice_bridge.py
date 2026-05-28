#!/usr/bin/env python3
"""终端 voice_dialog 与软件脸同步：轮询不写 API 时，网页读 last_reply.json。

用法（与 serve_hub 并行）:
  python3 scripts/avatar_voice_bridge.py

弘尊在另一终端跑:
  python3 scripts/voice_dialog.py

网页 avatar/index.html 每 500ms 拉取 avatar/last_reply.json 显示气泡。
本脚本仅打印最新答复（可选监视）。"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAST_REPLY = ROOT / "avatar" / "last_reply.json"


def main() -> int:
    print("软件脸桥接 · 监视 avatar/last_reply.json（Ctrl+C 停）")
    seen_ts = 0
    while True:
        if LAST_REPLY.is_file():
            try:
                data = json.loads(LAST_REPLY.read_text(encoding="utf-8"))
                ts = int(data.get("ts") or 0)
                if ts > seen_ts:
                    seen_ts = ts
                    print(f"\n【弘尊】{data.get('text', '')}")
                    print(f"【姜子牙】{data.get('reply', '')}")
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(0.5)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已停止")
        raise SystemExit(0) from None
