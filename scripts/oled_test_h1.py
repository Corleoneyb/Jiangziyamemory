#!/usr/bin/env python3
"""H1 · SSD1306 128x64 I2C 首屏测试（断电接线后再跑）。"""

from __future__ import annotations

import sys

try:
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
except ImportError:
    print("缺少 luma.oled：sudo apt install -y python3-luma.oled 或 pip3 install luma.oled")
    sys.exit(1)

ADDR = 0x3C  # 少数屏为 0x3D，失败可改


def main() -> int:
    serial = i2c(port=1, address=ADDR)
    device = ssd1306(serial)
    with canvas(device) as draw:
        draw.text((0, 0), "首星 Caesar", fill=255)
        draw.text((0, 18), "H1 OLED OK", fill=255)
    print(f"OLED OK (I2C 0x{ADDR:02X})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
