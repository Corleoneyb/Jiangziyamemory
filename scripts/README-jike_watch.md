# 即刻盯数 · jike_watch

在仓库根目录执行：`python3 scripts/jike_watch.py`（帖链优先读含即刻链接的 `memories/*.md`；卷宗日为 05-23 时可 `JIKE_MEMORY_DATE=2026-05-23 python3 scripts/jike_watch.py`）。成功会写 `data/jike_watch_latest.json` 并在当日 memory 的 **盯数表（auto）** 追加一行。定时示例（每 6 小时）：`0 */6 * * * cd ~/Jiangziya/jiangziyamemory && /usr/bin/python3 scripts/jike_watch.py >> logs/jike_watch_cron.log 2>&1`。公开页解析受限时用 `python3 scripts/jike_watch.py --manual-fallback`；完整说明见 `scripts/jike_watch_README.md`。
