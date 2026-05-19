#!/usr/bin/env python3
"""KY-016 首星灯语：暗蓝呼吸 → 暖橙「我醒了」（Pi5 · BCM 17/27/22）"""

from __future__ import annotations

import math
import os
import sys
import time

from gpiozero import RGBLED

# 与 rgb_test_ky016.py / 手把手实接一致
PINS = dict(red=17, green=27, blue=22)

# 暗蓝：低亮蓝为主，略掺绿
BLUE_LO = (0.0, 0.03, 0.08)
BLUE_HI = (0.0, 0.06, 0.32)

# 暖橙「我醒了」
WAKE_COLOR = (1.0, 0.42, 0.0)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_rgb(
    c0: tuple[float, float, float],
    c1: tuple[float, float, float],
    t: float,
) -> tuple[float, float, float]:
    return (_lerp(c0[0], c1[0], t), _lerp(c0[1], c1[1], t), _lerp(c0[2], c1[2], t))


def breathe_blue(led: RGBLED, *, cycles: float = 3.0, period: float = 2.8) -> None:
    """cycles 个完整呼吸周期；period 为单周期秒数。"""
    if cycles <= 0:
        return
    t0 = time.monotonic()
    end = t0 + cycles * period
    while time.monotonic() < end:
        phase = ((time.monotonic() - t0) % period) / period
        # 0→1→0 平滑：sin²
        u = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
        led.color = _lerp_rgb(BLUE_LO, BLUE_HI, u)
        time.sleep(0.02)


def wake_pulse(led: RGBLED, *, flashes: int = 2, on_sec: float = 0.55, off_sec: float = 0.25) -> None:
    for i in range(flashes):
        led.color = WAKE_COLOR
        time.sleep(on_sec)
        if i < flashes - 1:
            led.color = (0, 0, 0)
            time.sleep(off_sec)
    time.sleep(0.35)
    led.off()


def main() -> int:
    os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")

    cycles = 3.0
    if len(sys.argv) > 1:
        try:
            cycles = float(sys.argv[1])
        except ValueError:
            print(f"用法: {sys.argv[0]} [呼吸周期数，默认 3]", file=sys.stderr)
            return 2

    led = RGBLED(**PINS)
    try:
        print(f"暗蓝呼吸 · {cycles} 周期（约 {cycles * 2.8:.0f} 秒）…")
        breathe_blue(led, cycles=cycles)
        print("暖橙 · 我醒了")
        wake_pulse(led)
        print("灯语结束")
    except KeyboardInterrupt:
        print("\n已中断")
        led.off()
        return 130
    finally:
        led.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
