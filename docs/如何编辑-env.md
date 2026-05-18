# 如何编辑 `.env`（Cmd+P 搜不到时）

`.env` 以点开头，Cursor **快速打开经常显示空白**，不是你没有这个文件。

## 办法 1 · 终端用 nano（最简单）

```bash
cd ~/Jiangziya/Jiangziyamemory
nano .env
```

1. 光标移到 `PUSHPLUS_TOKEN=` **后面**，粘贴 token。  
2. 按 **Ctrl+O** 保存，**回车**，再 **Ctrl+X** 退出。

## 办法 2 · 用 Cursor 直接打开路径

菜单 **File → Open File…**（或 **Cmd+O**），粘贴路径：

```text
/Users/yangguang/Jiangziya/Jiangziyamemory/.env
```

## 办法 3 · 终端一键用 Cursor 打开

```bash
open -a Cursor /Users/yangguang/Jiangziya/Jiangziyamemory/.env
```

---

填好后在终端验证：

```bash
cd ~/Jiangziya/Jiangziyamemory
python3 scripts/fengshen_remind.py --dry-run
```

应显示 `通道: pushplus`。
