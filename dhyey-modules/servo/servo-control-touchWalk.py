#!/usr/bin/env python3

from gpiozero import AngularServo, DigitalInputDevice
import time

# ------------------------
# GPIO Configuration
# ------------------------
TOUCH_PIN = 17

LEFT_SERVO_PIN = 23
RIGHT_SERVO_PIN = 18      # Change if different

# ------------------------
# Servo Configuration
# ------------------------
REST = 0
STEP_ANGLE = 60
LEFT_FORWARD = STEP_ANGLE
RIGHT_FORWARD = -STEP_ANGLE

STEP_DELAY = 0.3
BETWEEN_STEPS = 0.2
TOTAL_STEPS = 7

# ------------------------
# Devices
# ------------------------
touch = DigitalInputDevice(
    TOUCH_PIN,
    pull_up=True,
    bounce_time=0.05
)

left_servo = AngularServo(
    LEFT_SERVO_PIN,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.0005,
    max_pulse_width=0.0024,
)

right_servo = AngularServo(
    RIGHT_SERVO_PIN,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.0005,
    max_pulse_width=0.0024,
)

left_servo.angle = REST
right_servo.angle = REST


def left_step():
    print("Left Step")

    left_servo.angle = LEFT_FORWARD
    time.sleep(STEP_DELAY)

    left_servo.angle = REST
    time.sleep(BETWEEN_STEPS)


def right_step():
    print("Right Step")

    right_servo.angle = RIGHT_FORWARD
    time.sleep(STEP_DELAY)

    right_servo.angle = REST
    time.sleep(BETWEEN_STEPS)


def walk():
    print("Walking...")

    for i in range(TOTAL_STEPS):
        if i % 2 == 0:
            left_step()
        else:
            right_step()

    print("Finished 8 steps")


print("Touch sensor ready...")

last_touch = False

try:
    while True:
        touched = not touch.value

        if touched and not last_touch:
            walk()

        last_touch = touched
        time.sleep(0.02)

except KeyboardInterrupt:
    left_servo.angle = REST
    right_servo.angle = REST
    print("Stopped")