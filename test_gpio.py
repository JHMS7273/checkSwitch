#!/usr/bin/env python3
"""
Direct GPIO pin test - no debounce, no logic inversion
"""

import time
from gpiozero import Device, DigitalInputDevice

try:
    from gpiozero.pins.lgpio import LGPIOFactory
except Exception:
    LGPIOFactory = None

if LGPIOFactory is not None:
    Device.pin_factory = LGPIOFactory()
else:
    print("Warning: LGPIOFactory unavailable; using default gpiozero pin factory")

# Test pin 11
pin = 11
print(f"Testing GPIO pin {pin}...")
print("This will show the raw pin state every second.")
print("Press Ctrl+C to stop.\n")

try:
    sensor = DigitalInputDevice(pin, pull_up=True)
    
    for i in range(60):  # 60 seconds
        value = sensor.value
        print(f"[{time.strftime('%H:%M:%S')}] Pin {pin}: {value}")
        time.sleep(1)
    
    sensor.close()
except Exception as e:
    print(f"ERROR: {e}")
