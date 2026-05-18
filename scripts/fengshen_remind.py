#!/usr/bin/env python3
"""封神物质提醒 MVP — PushPlus 或企业微信机器人出站一条。

密钥从环境变量或仓库根目录 .env 读取（.env 不入库）。
用法:
  python3 scripts/fengshen_remind.py
  python3 scripts/fengshen_remind.py --dry-run
  python3 scripts/fengshen_remind.py --message "自定义正文"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TITLE = "封神提醒"
DEFAULT_MESSAGE = "【封神总境】物质提醒通道试通 — 闻仲"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def send_pushplus(token: str, title: str, message: str) -> dict:
    url = "https://www.pushplus.plus/send"
    payload = {"token": token, "title": title, "content": message}
    return post_json(url, payload)


def send_wecom(webhook_key: str, message: str) -> dict:
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    payload = {"msgtype": "text", "text": {"content": message}}
    return post_json(url, payload)


def is_success(channel: str, result: dict) -> bool:
    if channel == "pushplus":
        return result.get("code") in (200, "200")
    if channel == "wecom":
        return result.get("errcode") == 0
    return False


def write_audit(carbon_id: str, channel: str) -> None:
    from datetime import date

    today = date.today().isoformat()
    mem = REPO_ROOT / "memories" / f"{today}.md"
    line = (
        f"\n🕐 物质提醒（{channel}）已向 **{carbon_id}** 发送试通，"
        f"{today} — 闻仲脚本 `scripts/fengshen_remind.py`\n"
    )
    if mem.is_file():
        mem.write_text(mem.read_text(encoding="utf-8").rstrip() + line + "\n", encoding="utf-8")
    else:
        mem.write_text(f"# {today}\n{line}", encoding="utf-8")
    print(f"审计已写入: {mem.relative_to(REPO_ROOT)}")


def pick_channel() -> tuple[str, dict]:
    pushplus = os.environ.get("PUSHPLUS_TOKEN", "").strip()
    wecom = os.environ.get("WECOM_WEBHOOK_KEY", "").strip()
    if pushplus:
        return "pushplus", {"token": pushplus}
    if wecom:
        return "wecom", {"key": wecom}
    return "", {}


def main() -> int:
    parser = argparse.ArgumentParser(description="封神物质提醒 MVP")
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="通知正文")
    parser.add_argument("--title", default=DEFAULT_TITLE, help="PushPlus 标题")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只检查配置，不发起网络请求",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="发送成功后向当日 memories 追加共卷审计一行",
    )
    parser.add_argument(
        "--carbon",
        default="闫滨",
        help="挂机律审计用碳标识，默认立境者",
    )
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    channel, creds = pick_channel()

    if not channel:
        print(
            "未配置提醒通道：请在仓库根目录创建 .env，设置 PUSHPLUS_TOKEN 或 WECOM_WEBHOOK_KEY。\n"
            "见 docs/提醒通道.md 与 .env.example",
            file=sys.stderr,
        )
        return 2

    print(f"通道: {channel}")
    if args.dry_run:
        print("dry-run: 配置已就绪，未发送。")
        return 0

    try:
        if channel == "pushplus":
            result = send_pushplus(creds["token"], args.title, args.message)
        else:
            result = send_wecom(creds["key"], args.message)
    except urllib.error.URLError as exc:
        print(f"发送失败: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if is_success(channel, result):
        print("发送成功。")
        return 0

    print("发送未成功，请核对 token/webhook 与 API 返回。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
