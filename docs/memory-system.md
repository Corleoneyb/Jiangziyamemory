# 灵台 · 记忆系统

柏鉴正神所掌。技术实现 = 本仓库 + **灵台**（`index.html`）+ 自动化脚本。

## 三线架构

| 节点 | 角色 | 状态 |
|------|------|------|
| **GitHub** | 主记忆库 | ✅ |
| **Gitee** | 国内镜像，GitHub Actions 自动同步 | ✅ |
| **海康智存** | 本地热备 | ⏳ 树莓派跑通后备份脚本 |

## 仓库约定

| 项目 | 说明 |
|------|------|
| GitHub 用户 | `Corleoneyb` |
| 仓库名 | **`Jiangziyamemory`**（注意大小写） |
| 网页入口 | https://corleoneyb.github.io/Jiangziyamemory/ |
| 代码仓库 | https://github.com/Corleoneyb/Jiangziyamemory |
| 日记忆目录 | `memories/YYYY-MM-DD.md` |
| 灵台（网页） | **`index.html`**（GitHub Pages 根目录） |
| Gitee 镜像 | `jiangziyamemory`（小写，Actions 同步） |
| 自动书记官 | `memory_keeper.py`（待升级实质总结，若已部署） |

正式地址一览 → [lingtai.md](lingtai.md)

## 灵台 `index.html`

- **灵台**：封神记忆读写入口（原称「见面台」）。  
- 浏览器打开 Pages：https://corleoneyb.github.io/Jiangziyamemory/  
- 或本地/仓库内打开 `index.html`，经 GitHub API 加载/写入记忆  
- 早期归档中的 `meet_jiang_ziya.html` 为旧文件名，现网以此文件为准  
- **按日期分文件**，下拉选择日期加载  
- **追加模式**：同日多次保存，内容追加到末尾，带时间戳 `🕐`，**永不覆盖**  
- **查看最新**：一键跳到最近有记忆的日期  
- **降级**：GitHub 不可用时显示本地核心记忆  

## 文档 vs 日记忆

| 类型 | 位置 | 用途 |
|------|------|------|
| 架构 / 神系 / 路线图 | `docs/*.md` | 稳定、可版本对比 |
| 日常流水 / 对话要点 | `memories/YYYY-MM-DD.md` | 追加、带时间戳 |

日记忆里用一行链接指向 `docs/` 即可，勿把长文架构重复粘贴进每日文件。

## 开卷 · 封卷（对话记忆协议）

Cursor 等对话 AI **无跨会话长期记忆**，上下文过长时还可能压缩较早内容。因此：

| 口令 | 作用 |
|------|------|
| **姜子牙，封神榜何在？** | 开卷：加载 `docs/`、最近 `memories/`，接续前缘 |
| **姜子牙，封卷入灵台** | 封卷：将本场已决/待办/未决写入当日 `memories/YYYY-MM-DD.md` 的 `## 🧾 封卷` |

**何时封卷**：收工前、新开聊天前、话题大切换前、感觉对话已很长、或 AI 开始遗忘前文时。  
**封卷要求**：有实质要点，禁止仅时间戳空话（与铁律一致）。  
**说明**：AI 收不到「即将压缩」的系统告警，靠主人节奏 + 口令，不靠机器提醒。

## 已废弃方案

- Firebase / LeanCloud / Supabase — 网络或注册问题  
- Simplenote 公开链接 — 跨域失败  

## 安全

- GitHub Token 仅配置在本地环境，**勿写入** markdown 或提交到仓库  
- 旧记忆残留曾导致灵台异常 — 已清理；今后删改记忆走 git 历史，灵台只做追加  
