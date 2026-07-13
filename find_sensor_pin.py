        #!/usr/bin/env python3
"""
Multi-pin test - finds which GPIO pin the sensor is connected to
"""

import argparse
import time

from gpiozero import Device, DigitalInputDevice

# Prefer the LGPIOFactory when available (faster native access), but allow
# the script to run without it so users who can't build `lgpio` can still
# detect pins using the default pin factory (RPi.GPIO or pigpio).
try:
    from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
    LGPIOFactory = None

if LGPIOFactory is not None:
    Device.pin_factory = LGPIOFactory()
else:
    # Defer to gpiozero's default pin factory. This will work if the
    # system has RPi.GPIO or pigpio available; no action required here.
    print("Warning: LGPIOFactory unavailable; using default gpiozero pin factory")

DEFAULT_PINS = [4, 17, 27, 22, 23, 24, 25]
DEFAULT_DURATION = 10.0
DEFAULT_INTERVAL = 0.2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect which BCM GPIO pin is wired to the digital sound sensor."
    )
    parser.add_argument(
        "--pins",
        type=int,
        nargs="+",
        default=DEFAULT_PINS,
        help="BCM GPIO pins to test (default: %(default)s)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION,
        help="Total seconds to sample each pin (default: %(default)s)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help="Seconds between samples (default: %(default)s)",
    )
    return parser.parse_args()


def analyze_pin(pin: int, duration: float, interval: float) -> tuple[set[int], int, int]:
    sensor = DigitalInputDevice(pin, pull_up=True)
    try:
        values: list[int] = []
        end_time = time.time() + duration
        while time.time() < end_time:
            values.append(int(sensor.value))
            time.sleep(interval)
        counts = (values.count(0), values.count(1))
        return set(values), counts[0], counts[1]
    finally:
        sensor.close()


def format_summary(pin: int, zeros: int, ones: int) -> str:
    total = zeros + ones
    if total == 0:
        return f"GPIO {pin}: no samples collected"

    if zeros and ones:
        return (
            f"GPIO {pin}: changed ({zeros} sound, {ones} quiet)"
        )
    if zeros:
        return f"GPIO {pin}: always LOW ({zeros}/{total}) — likely sound or always triggered"
    return f"GPIO {pin}: always HIGH ({ones}/{total}) — likely quiet or disconnected"


def main() -> int:
    args = parse_args()

    print("=" * 70)
    print("MULTI-PIN SENSOR DETECTION TEST")
    print("=" * 70)
    print(f"\nTesting GPIO pins: {', '.join(map(str, args.pins))}")
    print(f"Sampling each pin for {args.duration:.1f}s at {args.interval:.2f}s intervals...\n")

    results: dict[int, set[int]] = {}
    sample_counts: dict[int, tuple[int, int]] = {}

    for pin in args.pins:
        try:
            print(f"Testing GPIO {pin}...")
            values, zeros, ones = analyze_pin(pin, args.duration, args.interval)
            results[pin] = values
            sample_counts[pin] = (zeros, ones)

            if zeros and ones:
                print(f"  ✅ GPIO {pin}: VALUES CHANGED ({zeros} sound, {ones} quiet)")
            elif zeros:
                print(f"  ❌ GPIO {pin}: Always LOW ({zeros} samples) — likely sound or stuck")
            elif ones:
                print(f"  ❌ GPIO {pin}: Always HIGH ({ones} samples) — likely quiet or disconnected")
            else:
                print(f"  ? GPIO {pin}: No samples collected")
        except Exception as e:
            print(f"  ERROR GPIO {pin}: {e}")

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY:")
    print("=" * 70)

    best_pins = [pin for pin, vals in results.items() if len(vals) == 2]
    for pin in args.pins:
        if pin not in sample_counts:
            continue
        zeros, ones = sample_counts[pin]
        print(format_summary(pin, zeros, ones))

    if best_pins:
        print("\n✅ Likely sensor pins:")
        for pin in best_pins:
            print(f"  GPIO {pin}")
        print("\nUse: python sound_sensor.py --pin <GPIO>")
    else:
        print("\n❌ No GPIO pin showed state changes!")
        print("If GPIO 17 is wired, adjust the potentiometer until quiet room noise becomes HIGH and sound becomes LOW.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
