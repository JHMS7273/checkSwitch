#!/usr/bin/env python3
"""
Optional analog sound reading via MCP3008 ADC + KY-038 AO pin.

Use this when you need a numeric loudness level instead of on/off detection.
Requires an MCP3008 chip wired over SPI.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time

from gpiozero import Device, MCP3008
from gpiozero.pins.lgpio import LGPIOFactory

DEFAULT_CHANNEL = 0
DEFAULT_THRESHOLD = 0.15
DEFAULT_SAMPLE_INTERVAL = 0.1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read analog sound level from MCP3008 on Raspberry Pi 5."
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=DEFAULT_CHANNEL,
        choices=range(8),
        help=f"MCP3008 channel (0-7, default: {DEFAULT_CHANNEL})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Trigger when value exceeds this 0.0-1.0 level (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_SAMPLE_INTERVAL,
        help=f"Seconds between readings (default: {DEFAULT_SAMPLE_INTERVAL})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    Device.pin_factory = LGPIOFactory()

    adc = MCP3008(channel=args.channel)

    running = True

    def shutdown(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("Analog sound monitor started")
    print(f"  MCP3008 channel: {args.channel}")
    print(f"  Threshold:       {args.threshold}")
    print("  Press Ctrl+C to stop.\n")

    try:
        while running:
            level = adc.value
            status = "LOUD" if level >= args.threshold else "quiet"
            print(f"[{time.strftime('%H:%M:%S')}] level={level:.3f}  {status}")
            time.sleep(args.interval)
    finally:
        adc.close()
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
