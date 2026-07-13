#!/usr/bin/env python3
"""
Check whether a digital sound sensor is connected to a GPIO pin.

This script samples the configured BCM pin using an internal pull-up.
For a KY-038/LM393 sound sensor, the digital output is active-low:
- LOW (0) means sound detected or the sensor output is actively pulling the line low.
- HIGH (1) means quiet or an open/disconnected line.

If the pin stays HIGH, the sensor may be disconnected or simply quiet.
If the pin stays LOW, the sensor line is held active/low and may be stuck or miswired.
If the pin toggles between 0 and 1, the sensor appears connected and working.
"""

from __future__ import annotations

import argparse
import sys
import time

from gpiozero import Device, DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

DEFAULT_GPIO_PIN = 17
DEFAULT_SAMPLES = 10
DEFAULT_INTERVAL = 0.5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether a digital sound sensor is connected to a Raspberry Pi GPIO pin."
    )
    parser.add_argument(
        "--pin",
        type=int,
        default=DEFAULT_GPIO_PIN,
        help=f"BCM GPIO pin to test (default: {DEFAULT_GPIO_PIN})",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=DEFAULT_SAMPLES,
        help=f"Number of readings to sample (default: {DEFAULT_SAMPLES})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"Seconds between readings (default: {DEFAULT_INTERVAL})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    Device.pin_factory = LGPIOFactory()

    try:
        sensor = DigitalInputDevice(args.pin, pull_up=True)
    except Exception as exc:
        print(f"ERROR: Unable to initialize GPIO {args.pin}: {exc}")
        return 1

    print("GPIO connection check")
    print(f"  BCM pin: {args.pin}")
    print(f"  Samples: {args.samples}")
    print(f"  Interval: {args.interval}s")
    print("  Note: HIGH can mean quiet or disconnected; LOW means the sensor line is active.")
    print("  Make noise near the sensor while the script runs to test behavior.")
    print()

    values: list[int] = []

    try:
        for i in range(args.samples):
            value = sensor.value
            values.append(value)
            state = "LOW (active)" if value == 0 else "HIGH (quiet/open)"
            print(f"[{i + 1}/{args.samples}] {state}")
            time.sleep(args.interval)
    finally:
        sensor.close()

    unique_values = set(values)
    print()
    print("Summary:")
    if unique_values == {0}:
        print("  - Pin stayed LOW for all samples.")
        print("  - This means the sensor line is continuously active/low.")
        print("  - Check wiring, power, and the sensor module; it may be stuck or miswired.")
    elif unique_values == {1}:
        print("  - Pin stayed HIGH for all samples.")
        print("  - This can mean the sensor is quiet or disconnected.")
        print("  - If you expect noise, verify the DO wire and sensor power.")
        print("  - You can also unplug DO to confirm the pin remains HIGH when disconnected.")
    else:
        print("  - Pin changed between LOW and HIGH.")
        print("  - This suggests the sensor is connected and responding to sound.")
        print("  - If you see LOW when making noise and HIGH when quiet, the sensor is behaving correctly.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
