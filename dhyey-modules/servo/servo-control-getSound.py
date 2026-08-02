#!/usr/bin/env python3
"""Move an MG90S servo when a sound sensor on GPIO16 is triggered."""

from __future__ import annotations

import signal
import sys
import time

from gpiozero import AngularServo, Device, DigitalInputDevice

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
    LGPIOFactory = None

SOUND_PIN = 16
SERVO_PIN = 18
MOVE_ANGLE = 90  # full movement for the MG90S servo
MOVE_DURATION_SECONDS = 0.1  # how long the servo stays at the moved position
RETURN_DELAY_SECONDS = 0.1  # how long to wait before returning to center
DEBOUNCE_SECONDS = 0.05


def main() -> int:
    if LGPIOFactory is not None:
        Device.pin_factory = LGPIOFactory()

    try:
        sound_sensor = DigitalInputDevice(SOUND_PIN, pull_up=True, bounce_time=DEBOUNCE_SECONDS)
        servo = AngularServo(
            SERVO_PIN,
            min_pulse_width=0.0005,
            max_pulse_width=0.0024,
            min_angle=-90,
            max_angle=90,
        )
    except Exception as exc:
        print(f"ERROR: Could not initialize GPIO pins: {exc}")
        return 1

    running = True

    def stop(signum: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(f"Waiting for sound on GPIO{SOUND_PIN}... Press Ctrl+C to stop.")

    last_sound_detected = False
    try:
        while running:
            sound_detected = not sound_sensor.value

            if sound_detected and not last_sound_detected:
                print("Sound detected")
                servo.angle = MOVE_ANGLE
                time.sleep(MOVE_DURATION_SECONDS)
                servo.angle = 0
                time.sleep(RETURN_DELAY_SECONDS)

            last_sound_detected = sound_detected
            time.sleep(0.02)
    finally:
        servo.angle = 0
        sound_sensor.close()
        print("Stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
