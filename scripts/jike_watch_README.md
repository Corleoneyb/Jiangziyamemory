# 即刻盯数 MVP（T010）

> 工单：`tasks/赵公明-即刻盯数自动化.md` · 帖锚点见 `memories/2026-05-23.md`

## 一键试跑

```bash
cd ~/Jiangziya/Jiangziyamemory
python3 scripts/jike_watch.py --dry-run
python3 scripts/jike_watch.py
```

成功：终端打印 JSON；`memories/当日.md` 追加 **盯数表（auto）** 一行（备注含 `auto · jike_watch`）；日志 `logs/jike_watch_YYYYMMDD.log`（**勿提交 cookie**）。

## 环境变量（可选）

```bash
# .env
JIKE_POST_URL=https://web.okjike.com/u/.../post/...
```

失败时尝试调用 `scripts/fengshen_remind.py`（须已配 PushPlus）。

## 定时（Mac 示例）

```bash
# 每 6 小时
0 */6 * * * cd ~/Jiangziya/Jiangziyamemory && /usr/bin/python3 scripts/jike_watch.py >> logs/jike_watch_cron.log 2>&1
```

## 阶段 B（未做）

Playwright + 本机已登录 cookie → 私信/问价字段；见脚本头注释。
