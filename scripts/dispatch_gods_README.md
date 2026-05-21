# 诸神自动派单 · 脚本占位（T011）

> **状态**：未实现 — 工单见 [`tasks/闻仲-工单-诸神自动派单.md`](../tasks/闻仲-工单-诸神自动派单.md)  
> **今天**：弘尊仍手贴 [`tasks/诸神-立即落实-2026-05-23.md`](../tasks/诸神-立即落实-2026-05-23.md) 各派单块。

## 计划入口（闻仲填）

```bash
# 将来
python3 scripts/dispatch_gods.py          # 向各神 Agent 发送当日派单块
python3 scripts/dispatch_gods.py --dry-run  # 只打印将发给谁、正文长度
```

## 依赖（预期）

- 源：`tasks/诸神-立即落实-*.md`（取最新日期）
- 配置：`scripts/dispatch_gods_config.json`（神名 → Cursor agentId）
- 密钥：`CURSOR_API_KEY`
- SDK：`@cursor/sdk`（`Agent.resume` + `agent.send`）或 REST — 见闻仲 A 阶段调研

## 失败时

PushPlus 提醒 + 打印应立即手贴的文件路径。

---

*占位 · 2026-05-23 · 勿删*
