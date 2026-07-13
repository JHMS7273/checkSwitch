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

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
    LGPIOFactory = None

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

    # Prefer the native lgpio backend on Raspberry Pi 5 when available.
    if LGPIOFactory is not None:
        Device.pin_factory = LGPIOFactory()
    else:
        print("Warning: LGPIOFactory unavailable; using default gpiozero pin factory")

    try:
        sensor = DigitalInputDevice(
            args.pin,
            pull_up=True,
            bounce_time=args.debounce / 1000.0,
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize GPIO pin {args.pin}: {e}")
        print("This usually means:")
        print("  1. GPIO pin is already in use by another process")
        print("  2. You don't have permission to access GPIO")
        print("  3. The pin number is incorrect")
        return 1

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
    print("  Press Ctrl+C to stop.")
    print("  Debug: Raw sensor values (0=sound, 1=quiet):\n")

    last_state: bool | None = None
    sample_count = 0

    try:
        while running:
            # Sensor output: LOW (0) when sound detected, HIGH (1) when quiet
            # We need to invert: sound_detected should be True when sensor.value is 0
            sound_detected = not sensor.value

            # Print debug info every 20 samples
            sample_count += 1
            if sample_count % 20 == 0:
                state_str = "SOUND" if sound_detected else "quiet"
                raw_state = "LOW" if sensor.value == 0 else "HIGH"
                print(f"[{time.strftime('%H:%M:%S')}] Pin: {raw_state} ({sensor.value}) → {state_str}")

            if sound_detected != last_state:
                if sound_detected:
                    print(f"[{time.strftime('%H:%M:%S')}] >>> SOUND DETECTED <<<")
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
