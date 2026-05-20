#!/usr/bin/env python3
"""把弘尊红绿灯摘要推到微信（PushPlus / 企微，与 T004 同密钥）。

用法:
  python3 scripts/push_traffic_light.py
  python3 scripts/push_traffic_light.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAFFIC = ROOT / "tasks" / "弘尊红绿灯.md"


def parse_table(md: str) -> list[dict]:
    rows: list[dict] = []
    for line in md.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 6 or cells[0] == "序号":
            continue
        # 列序：序号 | 事项 | 准 | 续议 | 否 | 意见
        ok_cell = cells[2] if len(cells) > 2 else ""
        rows.append(
            {
                "id": cells[0],
                "title": cells[1],
                "ok": "☑" in ok_cell or "✓" in ok_cell,
                "note": cells[5] if len(cells) > 5 else "",
            }
        )
    return rows


def build_message() -> str:
    md = TRAFFIC.read_text(encoding="utf-8")
    rows = parse_table(md)
    lines = ["【封神·弘尊红绿灯】", ""]
    pending = [r for r in rows if not r["ok"]]
    done = [r for r in rows if r["ok"]]
    if pending:
        lines.append("待批：")
        for r in pending:
            lines.append(f"  {r['id']} {r['title']}")
    if done:
        lines.append("")
        lines.append("已批：")
        for r in done:
            note = f"（{r['note']}）" if r["note"] else ""
            lines.append(f"  {r['id']} {r['title']} 准{note}")
    lines.append("")
    lines.append("点开批阅：https://corleoneyb.github.io/Jiangziyamemory/piyue/")
    lines.append("点按钮后复制裁决，微信发给姜子牙")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    msg = build_message()
    if args.dry_run:
        print(msg)
        return 0
    script = ROOT / "scripts" / "fengshen_remind.py"
    r = subprocess.run(
        [sys.executable, str(script), "--message", msg, "--title", "封神·待批"],
        cwd=str(ROOT),
    )
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
