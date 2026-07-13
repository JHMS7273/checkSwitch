#!/usr/bin/env python3
"""
Sound sensor (KY-038) digital reader for Raspberry Pi.
GPIO16 connected to sound sensor DO (Digital Output) pin.
Detects sound events and measures frequency/intensity.
"""

from __future__ import annotations

import signal
import sys
import time
from collections import deque
from gpiozero import Device, DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

# Configuration
GPIO_PIN = 16
DEBOUNCE_MS = 10  # Debounce time in milliseconds
SAMPLE_WINDOW = 2  # seconds - measure sound detections in this window
MIN_DETECTIONS = 1  # minimum detections to register as sound


def setup_gpio() -> None:
    """Initialize GPIO using lgpio factory for Raspberry Pi 5."""
    try:
        Device.pin_factory = LGPIOFactory()
        print("✓ GPIO initialized with lgpio factory")
    except Exception as e:
        print(f"Warning: Could not use lgpio factory: {e}")
        print("  Falling back to default pin factory")


def calculate_decibel(detection_count: int, duration: float) -> float:
    """
    Convert detection frequency to pseudo-decibel scale.
    More detections = higher dB
    """
    if detection_count < 1:
        return 0.0
    
    # Frequency of detections per second
    frequency = detection_count / duration if duration > 0 else 0
    
    # Better dB calculation: scale frequency to dB range
    # 1 detection/2sec = ~20dB, more frequent = higher dB
    import math
    try:
        # Frequency-based dB: 20*log10(frequency) + offset
        db = 20 * math.log10(max(frequency, 0.25)) + 30
        return max(0, min(db, 100))  # Clamp between 0-100 dB
    except ValueError:
        return 0.0


def signal_handler(sig, frame) -> None:
    """Handle Ctrl+C gracefully."""
    print("\n\n✓ Sound sensor monitoring stopped")
    sys.exit(0)


def main() -> None:
    """Main loop to read and print sound events."""
    print("=" * 60)
    print("Sound Sensor (KY-038) Digital Reader")
    print("GPIO16 connected to sound sensor DO (Digital Output) pin")
    print("=" * 60)
    print(f"Window: {SAMPLE_WINDOW} seconds | Debounce: {DEBOUNCE_MS}ms")
    print("\n⚠️  IMPORTANT: Adjust the blue potentiometer on the sensor")
    print("   until the onboard LED toggles at your desired noise level\n")
    print("Reading raw GPIO state and detecting sound events...")
    print("Press Ctrl+C to stop\n")
    
    setup_gpio()
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create digital input with debounce
        sound_sensor = DigitalInputDevice(
            GPIO_PIN,
            pull_up=True,
            bounce_time=DEBOUNCE_MS / 1000.0
        )
        
        print(f"✓ Sound sensor ready on GPIO{GPIO_PIN}\n")
        
        detection_times = deque(maxlen=200)
        last_state = sound_sensor.is_active
        last_print_time = time.time()
        last_change_time = time.time()
        
        while True:
            current_time = time.time()
            current_state = sound_sensor.is_active
            
            # Detect state change (sound event)
            if current_state != last_state:
                detection_times.append(current_time)
                last_change_time = current_time
                last_state = current_state
                event_type = "HIGH→LOW" if current_state else "LOW→HIGH"
                print(f"  [EVENT] {event_type} at {current_time:.2f}")
            
            # Print summary every half second
            if current_time - last_print_time >= 0.5:
                # Count detections in window
                cutoff_time = current_time - SAMPLE_WINDOW
                active_detections = sum(1 for t in detection_times if t > cutoff_time)
                
                # Calculate decibel value
                decibel = calculate_decibel(active_detections, SAMPLE_WINDOW)
                
                # Visual indicator
                bar_length = int(decibel / 2.5)
                bar = "█" * min(bar_length, 20)
                
                status = "QUIET" if decibel < 25 else ("MODERATE" if decibel < 50 else "LOUD")
                pin_state = "HIGH" if current_state else "LOW"
                
                print(f"Pin: {pin_state} | Detections: {active_detections:2d} | dB: {decibel:6.2f} | {bar:20s} | {status}")
                last_print_time = current_time
            
            time.sleep(0.05)  # More frequent polling
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    finally:
        try:
            sound_sensor.close()
        except:
            pass


if __name__ == "__main__":
    main()
