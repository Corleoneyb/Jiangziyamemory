# 手把手 · 树莓派 SSH 连不上

> 对应 RGB/T003 前置。一次只做一步，做完回姜子牙。

---

## 现象：输入 `yes` 后立刻断开

```text
Connection closed by 192.168.x.x port 22
```

且**还没出现** `password:` 提示。

---

## 最常见原因：连错设备（优先查）

路由器里设备能 **ping 通**，不等于它是树莓派。

| MAC 前缀（前 6 位） | 常见厂商 | 是不是 Pi |
|---------------------|----------|-----------|
| **D8:3A:DD**、**DC:A6:32**、**E4:5F:01**、**B8:27:EB** | 树莓派基金会 | **是** |
| **88:A2:9E** 等 | Espressif（ESP32/8266） | **多半不是** |

主机名叫 **Caesar**、能 ping、但 MAC 是 Espressif → 很可能是 **别的智能硬件**，不是 Imager 刚烧的 Pi5。对它发 SSH 会被对方直接关掉，属正常。

**做法：** 在 **TP-Link → 无线终端 / 已连接设备** 里找 MAC 以 **D8:3A:DD** 等开头的设备，记下它的 **IP**，再 SSH。

---

## 其它可能（Pi 已确认时）

| 原因 | 说明 |
|------|------|
| Imager 未开 SSH | 重烧时在「自定义」里勾选 **启用 SSH** |
| 用户名不对 | 用 Imager 里设的**用户名**，不是固定 `pi` |
| 刚开机 WiFi 未就绪 | 通电等 **2～3 分钟** 再试 |
| 诊断 | Mac 上：`ssh -v 用户名@IP` 看断在哪一行 |

较少见：fail2ban（多次输错密码后）、路由器 AP 隔离（能 ping 但不能 22 — 你目前能到密钥提示，更像连错机）。

---

## 推荐排查顺序

### 第 1 步 · 在路由器里认真 Pi

1. Mac 与 Pi 连 **同一 TP-Link WiFi**（Imager 里填的 SSID）。  
2. 打开 TP-Link **无线终端**列表。  
3. 找 MAC **D8:3A:DD / DC:A6:32 / E4:5F:01 / B8:27:EB** 的设备。  
4. 记下 **IP**（不要先用 Caesar / 88:A2:9E 的 IP，除非确认它就是 Pi）。

### 第 2 步 · 用 IP 登录

```bash
ping -c 4 新IP
ssh -v Imager用户名@新IP
```

- 出现 `password:` → 输入 Imager 密码。  
- 仍 `Connection closed` → 把 `ssh -v` **最后 15 行**（勿含密码）发给姜子牙。

### 第 3 步 · 列表里没有 Pi 时（三选一）

| 你有 | 做法 |
|------|------|
| **网线** | Pi 网口插 TP-Link LAN，等 2 分钟，再看有线/无线列表 |
| **HDMI + 键盘** | 桌面连 WiFi，终端执行 `hostname -I`、`hostname` |
| **都没有** | Windows 上 Imager **重烧**，自定义里：WiFi + **启用 SSH** + 用户名密码 + 主机名 |

---

## 登录成功后（接 RGB 首星）

```bash
sudo apt-get install -y python3-gpiozero git
git clone https://github.com/Corleoneyb/Jiangziyamemory.git
cd Jiangziyamemory
python3 scripts/rgb_test_ky016.py
```

接线见 `docs/手把手-RGB首星.md`（`-`→9，`R`→11，`G`→13，`B`→15）。
