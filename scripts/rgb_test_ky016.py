#!/usr/bin/env python3
"""KY-016 最小亮灯测试（立境者 Pi5 实接脚位，2026-05-20）"""

from time import sleep

from gpiozero import RGBLED

# 模块丝印 → BCM（物理脚：-=9, R=11/17, G=13/27, B=15/22）
# 共阴模块：GPIO 高电平亮（gpiozero 默认 active_high=True）
led = RGBLED(red=17, green=27, blue=22)

try:
    print("红 2 秒…")
    led.color = (1, 0, 0)
    sleep(2)
    print("绿 2 秒…")
    led.color = (0, 1, 0)
    sleep(2)
    print("蓝 2 秒…")
    led.color = (0, 0, 1)
    sleep(2)
    print("灭")
    led.off()
finally:
    led.close()
