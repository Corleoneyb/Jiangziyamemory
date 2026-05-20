# 殿址机 · 睡前并行 SOP（阶段 B1 交付）

> 解决难点：「24h 没人自动点 Agent」的**不花钱降级办法**。  
> 弘尊睡前 **15 分钟**；诸神出稿落 `deliverables/`。

## 弘尊（≤5 分钟）

1. 对本对话说：**「启动并行」** 或 **「执行今日工单」**  
2. 姜子牙回复今晚 **最多 3 个 Agent 名 + 粘贴块**  
3. 殿址机 Cursor 开 **3 个 New Agent**，各贴一块，各跑一轮  

## 殿址机（≤10 分钟）

| 窗口 | 粘贴 | 跑完标志 |
|------|------|----------|
| 比干 | `docs/agents/比干.md` + `tasks/比干-工单-*.md` | `deliverables/比干/` 有新 commit |
| 吴道子 | 同上模式 | `deliverables/吴道子/` |
| 赵公明/范蠡/闻仲 | 按姜子牙当晚指定 | 对应 deliverables 或 tasks |

## 验收（早上）

- 打开 `tasks/晨间裁决-日期.md`（柏鉴 cron）  
- 或 `deliverables/` 看新文件  
- 弘尊只批 **P0 / 红绿灯**，不全读  

## 不能替代

- Cursor **不会**自己半夜点 New Agent → 本 SOP 是现阶段办法  
- 若日后有 Background Agents / CLI，闻仲改 SOP v2  

*阶段 B 任务 B2 交付物*
