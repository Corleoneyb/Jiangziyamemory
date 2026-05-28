#!/usr/bin/env python3
"""H1 · SSD1306 亮屏测试（不写字，避免 PIL 字体版本问题）。"""

from __future__ import annotations

import sys

try:
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
except ImportError:
    print("缺少 luma.oled：sudo apt install -y python3-luma.oled")
    sys.exit(1)

ADDR = 0x3C


def main() -> int:
    serial = i2c(port=1, address=ADDR)
    device = ssd1306(serial)
    device.clear()
    with canvas(device) as draw:
        # 白框 + 斜线 = 肉眼可见，无需字体
        draw.rectangle(device.bounding_box, outline=255, fill=0)
        draw.line((0, 0, device.width - 1, device.height - 1), fill=255)
        draw.line((device.width - 1, 0, 0, device.height - 1), fill=255)
    print(f"OLED OK (I2C 0x{ADDR:02X}) — look for X on screen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
