#!/usr/bin/env python3
"""同步「弘尊批阅」到桌面：生成 WPS/Word 可直接双击的 .doc 文件（Mac 用 textutil）。

用法:
  python3 scripts/sync_desktop_bingyue.py
  python3 scripts/sync_desktop_bingyue.py --desktop ~/Desktop
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESKTOP = Path.home() / "Desktop" / "封神批阅"


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def wrap_html(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>{html_escape(title)}</title>
<style>body{{font-family:"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.65;padding:20px;}}
h1{{font-size:18pt;}} h2{{font-size:14pt;margin-top:16px;}} table{{border-collapse:collapse;width:100%;}}
td,th{{border:1px solid #999;padding:6px;}} .ok{{color:green;font-weight:bold;}}</style></head>
<body>{body_html}</body></html>"""


def build_traffic_light_html() -> str:
    src = (ROOT / "tasks" / "弘尊红绿灯.md").read_text(encoding="utf-8")
    body = f"<h1>弘尊红绿灯 · 批阅台</h1><p>仓库路径：tasks/弘尊红绿灯.md</p><pre>{html_escape(src)}</pre>"
    return wrap_html("弘尊红绿灯", body)


def build_biguan_summary_html() -> str:
    body = """
<h1>门 v2 文案 · 比干改稿（弘尊已批要点）</h1>
<h2>第一屏</h2>
<p>副标题：灵台记史，此处入境…；辅行：轻触门环 · 有声效；底注：首星已通灵</p>
<h2>诸神殿</h2>
<p>新增两行引言（OS 界面 / 非文件夹）</p>
<h2>神卡</h2>
<p>每神增加「一句」主文案；duty 略收紧；首星补灯语同调</p>
<h2>区块</h2>
<p>封神榜、今日纪事增加空态句</p>
<h2>入门故事</h2>
<p>闫滨视角：灵台＝桌子、门＝影院式入境；写入 v2 铃、暗场、殿上浮、四卡一句、底栏回灵台；收束于弘尊说「准」</p>
<p class="ok">裁决：准（2026-05-20 弘尊）</p>
<p>完整稿见仓库 deliverables/比干/门v2文案.md</p>
"""
    return wrap_html("门v2文案-比干", body)


def build_wudaozi_summary_html() -> str:
    body = """
<h1>门 v2 风格板 · 吴道子交付要点</h1>
<h2>相对 v0.1</h2>
<p>门外像门口，门内像浮出世。远星/中雾/vignette 三层；门框剪影；比干文案落位；暗场 0.35s 后界内上浮 24px。</p>
<h2>立绘阶段 A</h2>
<p>姜子牙榜轴、闻仲盔、魔礼青竖目、首星双晕灯+GPIO十字。详见 deliverables/吴道子/立绘升级.md</p>
<h2>闻仲待办（已准后执行）</h2>
<ul>
<li>更新 :root、三层星尘、.gate-frame、过渡 JS</li>
<li>写入比干文案</li>
<li>替换四卡 SVG</li>
<li>音效三角波+低音；可选 ambient_gate.mp3</li>
<li>魔礼青验收</li>
</ul>
<p class="ok">裁决：准（2026-05-20 弘尊）</p>
"""
    return wrap_html("门v2风格板-吴道子", body)


def html_to_doc(html_path: Path, doc_path: Path) -> bool:
    try:
        subprocess.run(
            ["textutil", "-convert", "doc", "-output", str(doc_path), str(html_path)],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  textutil 失败（非 Mac 或无 textutil）：{e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--desktop", type=Path, default=DEFAULT_DESKTOP)
    args = parser.parse_args()
    out_dir: Path = args.desktop
    out_dir.mkdir(parents=True, exist_ok=True)

    items = [
        ("弘尊红绿灯", build_traffic_light_html()),
        ("门v2文案-比干-批阅摘要", build_biguan_summary_html()),
        ("门v2风格板-吴道子-批阅摘要", build_wudaozi_summary_html()),
    ]

    tmp = out_dir / "_tmp_html"
    tmp.mkdir(exist_ok=True)
    made: list[str] = []

    for name, html in items:
        html_p = tmp / f"{name}.html"
        doc_p = out_dir / f"{name}.doc"
        html_p.write_text(html, encoding="utf-8")
        if html_to_doc(html_p, doc_p):
            made.append(str(doc_p))
        else:
            #  fallback: copy html for browser/WPS open
            fallback = out_dir / f"{name}.htm"
            shutil.copy(html_p, fallback)
            made.append(str(fallback))

    # 复制可直接打开的 htm 全文（比干/吴道子若仓库有）
    for rel in [
        "deliverables/比干/门v2文案-WPS.htm",
        "deliverables/吴道子/门V2风格板-WPS.html",
        "deliverables/比干/入门故事.md",
    ]:
        src = ROOT / rel
        if src.is_file():
            dest = out_dir / src.name
            shutil.copy(src, dest)
            made.append(str(dest))

    readme = out_dir / "请先读我.txt"
    readme.write_text(
        "封神批阅文件夹\n\n"
        "双击 .doc 用 WPS 或 Word 打开（Mac 已用系统转换）。\n"
        "若只有 .htm，WPS 里：文件 → 打开 → 选该文件。\n\n"
        "批完在仓库 tasks/弘尊红绿灯.md 打勾，或微信回复姜子牙。\n"
        "推微信：在仓库目录运行 python3 scripts/push_traffic_light.py\n",
        encoding="utf-8",
    )
    print(f"【桌面批阅】已同步到：{out_dir}")
    for m in made:
        print(f"  · {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
