#!/usr/bin/env python3
"""
Hardware diagnostic - test if KY-038 sensor is connected properly
"""

import time
from gpiozero import Device, DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

print("=" * 60)
print("KY-038 SENSOR HARDWARE DIAGNOSTIC")
print("=" * 60)
print("\nTesting GPIO pin 17...\n")

try:
    sensor = DigitalInputDevice(17, pull_up=True)
    
    print("Sensor initialized successfully!")
    print("\nNow testing pin state changes...")
    print("Watch for transitions between 0 (SOUND) and 1 (QUIET)")
    print("If you see ONLY 0 or ONLY 1, there's a wiring problem.\n")
    
    values_seen = set()
    
    for i in range(120):  # 120 seconds
        value = sensor.value
        values_seen.add(value)
        
        state_str = "LOW  (SOUND)" if value == 0 else "HIGH (quiet)"
        print(f"[{time.strftime('%H:%M:%S')}] Pin 11: {state_str}")
        
        time.sleep(1)
    
    sensor.close()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC RESULTS:")
    print("=" * 60)
    
    if len(values_seen) == 2:
        print("✅ GOOD: Pin changed between 0 and 1")
        print("   The sensor IS working. Adjust potentiometer or check audio volume.")
    elif 0 in values_seen and 1 not in values_seen:
        print("❌ PROBLEM: Pin is stuck at LOW (0)")
        print("   → Check VCC wire connection")
        print("   → Sensor might be powered incorrectly")
    elif 1 in values_seen and 0 not in values_seen:
        print("❌ PROBLEM: Pin is stuck at HIGH (1)")
        print("   → Check GND wire connection")
        print("   → Check DO wire connection to GPIO 17")
    else:
        print("❌ PROBLEM: Pin never initialized")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("GPIO pin 17 might already be in use.")
