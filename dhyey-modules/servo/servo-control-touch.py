#!/usr/bin/env python3
"""Move an MG90S servo when a touch sensor on GPIO17 is triggered."""

from __future__ import annotations

import signal
import sys
import time

from gpiozero import AngularServo, Device, DigitalInputDevice

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
    LGPIOFactory = None

TOUCH_PIN = 17
SERVO_PINS = (18, 23)
MOVE_ANGLE = 90 #25% of a 180 degree range, which is the max for an MG90S servo
MOVE_DURATION_SECONDS = 0.1  # how long the servos stay at the moved position
RETURN_DELAY_SECONDS = 0.1  # how long to wait before returning to center
DEBOUNCE_SECONDS = 0.05


def main() -> int:
    if LGPIOFactory is not None:
        Device.pin_factory = LGPIOFactory()

    try:
        touch = DigitalInputDevice(TOUCH_PIN, pull_up=True, bounce_time=DEBOUNCE_SECONDS)
        servos = [
            AngularServo(
                pin,
                min_pulse_width=0.0005,
                max_pulse_width=0.0024,
                min_angle=-90,
                max_angle=90,
            )
            for pin in SERVO_PINS
        ]
    except Exception as exc:
        print(f"ERROR: Could not initialize GPIO pins: {exc}")
        return 1

    running = True

    def stop(signum: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(f"Waiting for touch on GPIO{TOUCH_PIN}... Press Ctrl+C to stop.")

    last_touched = False
    try:
        while running:
            touched = not touch.value

            if touched and not last_touched:
                print("Touch detected")
                for servo in servos:
                    servo.angle = MOVE_ANGLE
                time.sleep(MOVE_DURATION_SECONDS)
                for servo in servos:
                    servo.angle = 0
                time.sleep(RETURN_DELAY_SECONDS)

            last_touched = touched
            time.sleep(0.02)
    finally:
        for servo in servos:
            servo.angle = 0
        touch.close()
        print("Stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
