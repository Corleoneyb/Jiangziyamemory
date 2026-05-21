#!/usr/bin/env python3
"""即刻帖盯数 MVP（T010）— 从当日 memory 读帖链，拉公开页或占位，写 JSON + memory 表。

阶段 A：HTTP 拉帖 URL，解析有限字段，追加 JSON 行 + memory 表行（标记 auto / manual-fallback）。
阶段 B：Playwright + cookie（见 README-jike_watch.md）。

用法:
  python3 scripts/jike_watch.py --dry-run
  python3 scripts/jike_watch.py
  python3 scripts/jike_watch.py --post-url 'https://web.okjike.com/...'
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POST = (
    "https://web.okjike.com/u/46618ef9-2328-4d62-9342-e0c9b9c967db/"
    "post/6a0e4c4763725fe7e5a34625"
)
LOG_DIR = REPO_ROOT / "logs"
DATA_DIR = REPO_ROOT / "data"
LATEST_JSON = DATA_DIR / "jike_watch_latest.json"
STATE_FILE = LOG_DIR / "jike_watch_state.json"
JIKE_URL_RE = re.compile(r"https://web\.okjike\.com/[^\s\)>\"']+")


def today_memory_path() -> Path:
    d = datetime.now()
    name = f"{d.year}-{d.month:02d}-{d.day:02d}.md"
    return REPO_ROOT / "memories" / name


def watch_memory_path() -> Path:
    """盯数写入目标：JIKE_MEMORY_DATE > 当日含帖链 > 最新含帖链的 memory。"""
    override = os.environ.get("JIKE_MEMORY_DATE")
    if override:
        return REPO_ROOT / "memories" / f"{override}.md"
    today = today_memory_path()
    if today.is_file() and JIKE_URL_RE.search(today.read_text(encoding="utf-8")):
        return today
    mem_dir = REPO_ROOT / "memories"
    for p in sorted(mem_dir.glob("20*.md"), reverse=True):
        try:
            if JIKE_URL_RE.search(p.read_text(encoding="utf-8")):
                return p
        except OSError:
            continue
    return today


def post_url_from_memory(path: Path | None = None) -> str | None:
    """从 memory 首发帖段落读取即刻链接。"""
    path = path or watch_memory_path()
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    m = JIKE_URL_RE.search(text)
    return m.group(0).rstrip(".,;") if m else None


def resolve_post_url(cli_url: str | None) -> tuple[str, str]:
    """返回 (url, resolved_from)：cli | env | memory | default。"""
    if cli_url:
        return cli_url, "cli"
    env = os.environ.get("JIKE_POST_URL")
    if env:
        return env, "env"
    mem = post_url_from_memory()
    if mem:
        return mem, "memory"
    return DEFAULT_POST, "default"


def load_dotenv() -> None:
    env = REPO_ROOT / ".env"
    if not env.is_file():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def fetch_url(url: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; FengshenWatch/0.1; +https://github.com/Corleoneyb/Jiangziyamemory)",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def guess_counts(html: str) -> dict:
    """公开页启发式；SPA/登录墙时常为 0，须 B 阶段 Playwright 补强。"""
    comment = 0
    limited = False
    if len(html) < 800 or "login" in html.lower() and "commentCount" not in html:
        limited = True
    for pat in (
        r'"commentCount"\s*:\s*(\d+)',
        r"commentCount[\"']?\s*[:=]\s*(\d+)",
        r"(\d+)\s*条评论",
    ):
        m = re.search(pat, html)
        if m:
            comment = int(m.group(1))
            break
    return {
        "comment": comment,
        "dm": "—",
        "price_ask": "—",
        "parse": "heuristic",
        "limited": limited,
    }


def write_latest_json(payload: dict, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run] would write", LATEST_JSON)
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", LATEST_JSON)


def append_memory_row(row: dict, dry_run: bool) -> None:
    path = watch_memory_path()
    source = row.get("source", "auto")
    line = (
        f"| {row['time']} | {row['comment']} | {row['dm']} | {row['price_ask']} | "
        f"{source} · jike_watch · {row.get('note', '')} |"
    )
    if dry_run:
        print("[dry-run] would append to", path)
        print(line)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.is_file() else f"# {path.stem}\n\n"
    if "jike_watch" in text and row["time"] in text:
        print("Skip duplicate row for", row["time"])
        return
    if "## 盯数表（auto）" not in text:
        text += "\n## 盯数表（auto）\n\n| 时点 | 评论 | 私信 | 问价 | 备注 |\n|------|:----:|:----:|:----:|------|\n"
    text += line + "\n"
    path.write_text(text, encoding="utf-8")
    print("Appended memory row:", path)


def write_log(payload: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"jike_watch_{datetime.now().strftime('%Y%m%d')}.log"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    STATE_FILE.write_text(
        json.dumps(
            {"last_run": payload["time"], "last_status": payload["status"], "source": payload.get("source")},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def notify_fail(msg: str) -> None:
    script = REPO_ROOT / "scripts" / "fengshen_remind.py"
    if script.is_file():
        os.system(
            f'{sys.executable} "{script}" --message "[封神] 即刻盯数失败: {msg[:120]}"'
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="即刻帖盯数 MVP")
    parser.add_argument("--post-url", default=None, help="覆盖 memory/默认帖链")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--manual-fallback",
        action="store_true",
        help="不拉页，写占位 JSON+表行（公开页不可解析时）",
    )
    args = parser.parse_args()
    load_dotenv()

    post_url, resolved_from = resolve_post_url(args.post_url)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    payload: dict = {
        "time": now,
        "url": post_url,
        "url_source": resolved_from,
        "status": "ok",
        "source": "auto",
        "limitation": None,
    }

    if args.manual_fallback:
        payload["status"] = "stub"
        payload["source"] = "manual-fallback"
        payload["limitation"] = "公开页未拉取；弘尊可 App 看一眼后口述，或等 Playwright B 阶段"
        counts = {"comment": "—", "dm": "—", "price_ask": "—", "parse": "manual-fallback"}
        payload["counts"] = counts
    else:
        try:
            status, html = fetch_url(post_url)
            payload["http_status"] = status
            counts = guess_counts(html)
            payload["counts"] = counts
            if counts.get("limited"):
                payload["source"] = "manual-fallback"
                payload["limitation"] = (
                    "HTTP 200 但公开 HTML 可能为 SPA/登录墙，评论数不可靠；"
                    "见 scripts/README-jike_watch.md 阶段 B"
                )
        except urllib.error.URLError as exc:
            payload["status"] = "fail"
            payload["source"] = "manual-fallback"
            payload["error"] = str(exc)
            payload["limitation"] = "fetch_failed"
            counts = {"comment": "—", "dm": "—", "price_ask": "—", "parse": "error"}
            payload["counts"] = counts
            write_latest_json(payload, args.dry_run)
            write_log(payload)
            if not args.dry_run:
                notify_fail(str(exc))
                row = {
                    "time": now,
                    "comment": "—",
                    "dm": "—",
                    "price_ask": "—",
                    "note": "fetch_fail",
                    "source": "manual-fallback",
                }
                append_memory_row(row, args.dry_run)
            print("Fetch failed:", exc, file=sys.stderr)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1

    row = {
        "time": now,
        "comment": str(counts.get("comment", "—")),
        "dm": counts.get("dm", "—"),
        "price_ask": counts.get("price_ask", "—"),
        "note": f"http={payload.get('http_status', 'stub')} url_from={resolved_from}",
        "source": payload["source"],
    }
    append_memory_row(row, args.dry_run)
    write_latest_json(payload, args.dry_run)
    write_log(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
