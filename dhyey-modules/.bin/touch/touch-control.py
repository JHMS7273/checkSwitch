#!/usr/bin/env python3
"""Print TOUCH when a digital touch sensor on GPIO17 is triggered."""

from __future__ import annotations

import signal
import sys
import time

from gpiozero import Device, DigitalInputDevice

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
    LGPIOFactory = None

GPIO_PIN = 17
DEBOUNCE_SECONDS = 0.05


def main() -> int:
    if LGPIOFactory is not None:
        Device.pin_factory = LGPIOFactory()

    try:
        touch = DigitalInputDevice(GPIO_PIN, pull_up=True, bounce_time=DEBOUNCE_SECONDS)
    except Exception as exc:
        print(f"ERROR: Could not initialize GPIO{GPIO_PIN}: {exc}")
        return 1

    running = True

    def stop(signum: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(f"Listening for touch on GPIO{GPIO_PIN}... Press Ctrl+C to stop.")

    last_value: bool | None = None
    try:
        while running:
            # Many touch modules pull the line LOW when touched.
            touched = not touch.value

            if touched and last_value is not True:
                print("TOUCH")

            last_value = touched
            time.sleep(0.02)
    finally:
        touch.close()
        print("Stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
