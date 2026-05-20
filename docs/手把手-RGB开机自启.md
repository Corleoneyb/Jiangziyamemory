# 手把手 · Pi 开机自启灯语

> 对应待办 **T008**。Pi5 **Caesar**，脚本 `~/rgb_breath.py` 已能手动跑通后再做。**一次一步**。

---

## 前提

- [ ] Mac 与 Pi **同一 WiFi**（同网段）  
- [ ] `~/rgb_breath.py` 在 Pi 上存在且手动运行正常  
- [ ] 接线未变：RGB 9/11/13/15，风扇 4/6  

---

## 第 1 步 · Mac 传 service 文件

```bash
scp /Users/yangguang/Jiangziya/jiangziyamemory/scripts/rgb_breath.service caesar@192.168.10.179:~/
```

（IP 以路由器里 Caesar 为准。）

---

## 第 2 步 · SSH 进 Pi，安装 systemd 服务

```bash
ssh caesar@192.168.10.179
```

在 Pi 上逐条：

```bash
sudo cp ~/rgb_breath.service /etc/systemd/system/rgb_breath.service
sudo systemctl daemon-reload
sudo systemctl enable rgb_breath.service
sudo systemctl start rgb_breath.service
```

应看到灯：**暗蓝呼吸 → 暖橙**（与手动跑相同）。

查看状态（可选）：

```bash
systemctl status rgb_breath.service
```

---

## 第 3 步 · 试「重启后自动亮」

```bash
sudo reboot
```

等 2～3 分钟，**不用 SSH**，看 Pi 上电后是否自动跑一遍灯语。

> 若重启后没亮：SSH 回来执行 `journalctl -u rgb_breath.service -n 30` 把输出贴姜子牙。

---

## 第 4 步 · 待验收

榜面 T008 改 **待验收** → 魔礼青按 [`docs/手把手-T008验收清单.md`](手把手-T008验收清单.md) 收证据 → 发 **【魔礼青验收】T008**。

---

## 注意

- 这是 **开机跑一次** 灯语（oneshot），不是常驻呼吸；常驻需另开 T009。  
- 用户名若不是 `caesar`，改 service 里 `User=` 和 `ExecStart` 路径后再 `daemon-reload`。

---

*首星在，开机即应。*
