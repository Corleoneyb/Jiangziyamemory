#!/usr/bin/env python3
"""柏鉴 · 灵台日摘要（写死程序，可 cron 定时跑）

读 memories/今日.md + tasks/待办榜.md → 写 tasks/晨间裁决-YYYY-MM-DD.md
弘尊打开即见「诸神产出 + 待你批红绿灯」。

用法:
  python3 scripts/bailian_digest.py
  python3 scripts/bailian_digest.py --date 2026-05-21
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORIES = ROOT / "memories"
TASKS = ROOT / "tasks"
DELIVERABLES = ROOT / "deliverables"


def today_str(d: date | None = None) -> str:
    d = d or date.today()
    return d.isoformat()


def read_text(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def extract_todos(md: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in md.splitlines():
        if not line.startswith("| T"):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) >= 4 and cells[0].startswith("T"):
            rows.append((cells[0], cells[1], cells[3]))
    return rows


def list_deliverables() -> list[str]:
    out: list[str] = []
    if not DELIVERABLES.is_dir():
        return out
    for p in sorted(DELIVERABLES.rglob("*.md")):
        rel = p.relative_to(ROOT)
        out.append(str(rel))
    return out


def summarize_memory(md: str, max_lines: int = 40) -> str:
    if not md.strip():
        return "（今日记忆卷尚空）"
    lines = [ln for ln in md.splitlines() if ln.strip()]
    # 优先带 🕐 的行
    marked = [ln for ln in lines if "🕐" in ln or ln.startswith("##")]
    body = marked if marked else lines
    text = "\n".join(body[:max_lines])
    if len(body) > max_lines:
        text += "\n\n…（柏鉴摘要截断，全文见 memories/）"
    return text


def build_digest(for_date: str) -> str:
    mem_path = MEMORIES / f"{for_date}.md"
    board_path = TASKS / "待办榜.md"
    mem = read_text(mem_path)
    board = read_text(board_path)
    todos = extract_todos(board)
    dels = list_deliverables()

    pending = [t for t in todos if "待验收" in t[2] or "进行中" in t[2] or "待办" in t[2]]
    done = [t for t in todos if "已完成" in t[2]]

    lines = [
        f"# 晨间裁决 · {for_date}",
        "",
        "> **柏鉴自动生成** · 弘尊只做红绿灯：准 / 续议 / 否",
        "",
        "## 一、今日记忆摘要",
        "",
        summarize_memory(mem),
        "",
        "## 二、封神榜快照",
        "",
        f"- 已完成：**{len(done)}** 项",
        f"- 待动：**{len(pending)}** 项",
        "",
    ]
    if pending:
        lines.append("| 编号 | 事项 | 状态 | 弘尊批 |")
        lines.append("|------|------|------|----------|")
        for tid, title, state in pending:
            lines.append(f"| {tid} | {title} | {state} | ☐ 准 ☐ 续议 ☐ 否 |")
        lines.append("")

    lines.extend(["## 三、诸神 deliverables 目录", ""])
    if dels:
        for d in dels:
            lines.append(f"- `{d}`")
    else:
        lines.append("（尚无 deliverables，诸神并行工单见 `tasks/诸神并行工单.md`）")
    lines.extend([
        "",
        "## 四、弘尊 10 分钟",
        "",
        "1. 上表勾选 **准 / 续议 / 否**",
        "2. 对「准」项说：**闻仲执行**（或开闻仲 Agent）",
        "3. 不必自己写代码",
        "",
        "## 五、弘尊红绿灯（主表）",
        "",
        "人工批阅、勾选、意见：**`tasks/弘尊红绿灯.md`**（与聊天无关，姜子牙执行前只认此文件）。",
        "",
        "---",
        "",
        f"*生成：scripts/bailian_digest.py · 灵台 {for_date}*",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="柏鉴日摘要")
    parser.add_argument("--date", help="YYYY-MM-DD，默认今天")
    args = parser.parse_args()
    for_date = args.date or today_str()
    out = TASKS / f"晨间裁决-{for_date}.md"
    out.write_text(build_digest(for_date), encoding="utf-8")
    print(f"【柏鉴摘要】已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
