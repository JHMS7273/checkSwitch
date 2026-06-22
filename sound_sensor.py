#!/usr/bin/env python3
"""
KY-038 / LM393 sound sensor reader for Raspberry Pi 5.

Uses the digital output (DO) pin — loudest when the built-in potentiometer
threshold is exceeded. Adjust the blue screw on the module until the onboard
LED toggles at the noise level you care about.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time

from gpiozero import Device, DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

# BCM pin numbers (not physical pin numbers)
DEFAULT_GPIO_PIN = 17
DEFAULT_DEBOUNCE_MS = 50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor a digital sound sensor on Raspberry Pi 5."
    )
    parser.add_argument(
        "--pin",
        type=int,
        default=DEFAULT_GPIO_PIN,
        help=f"BCM GPIO pin connected to sensor DO (default: {DEFAULT_GPIO_PIN})",
    )
    parser.add_argument(
        "--debounce",
        type=int,
        default=DEFAULT_DEBOUNCE_MS,
        help="Debounce time in milliseconds (default: 50)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print when sound is detected (no idle messages)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Pi 5 needs the lgpio backend (stock RPi.GPIO does not support Pi 5).
    Device.pin_factory = LGPIOFactory()

    sensor = DigitalInputDevice(
        args.pin,
        pull_up=True,
        bounce_time=args.debounce / 1000.0,
    )

    running = True

    def shutdown(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("Sound sensor monitor started")
    print(f"  GPIO (BCM): {args.pin}")
    print(f"  Debounce:   {args.debounce} ms")
    print("  Adjust the potentiometer on the module until the LED reacts to your target noise.")
    print("  Press Ctrl+C to stop.\n")

    last_state: bool | None = None

    try:
        while running:
            # DO is active LOW on most KY-038 boards when sound exceeds threshold.
            sound_detected = not sensor.value

            if sound_detected != last_state:
                if sound_detected:
                    print(f"[{time.strftime('%H:%M:%S')}] SOUND DETECTED")
                elif not args.quiet:
                    print(f"[{time.strftime('%H:%M:%S')}] quiet")
                last_state = sound_detected

            time.sleep(0.05)
    finally:
        sensor.close()
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
