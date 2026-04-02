#!/usr/bin/env python3
"""Gesture detection demo for APDS9960 on Raspberry Pi 5.

Wiring:
    APDS9960  ->  Raspberry Pi
    VIN       ->  3.3V (Pin 1)
    GND       ->  GND  (Pin 6)
    SDA       ->  SDA  (Pin 3 / GPIO 2)
    SCL       ->  SCL  (Pin 5 / GPIO 3)

Make sure I2C is enabled:
    sudo raspi-config -> Interface Options -> I2C -> Enable

Install dependencies:
    pip install smbus2

Usage:
    python3 gesture_demo.py
"""

import time
from apds9960 import APDS9960

def main():
    print("APDS9960 Gesture Demo")
    print("=" * 40)
    print("Bewege deine Hand über den Sensor...")
    print("Drücke Ctrl+C zum Beenden.\n")

    with APDS9960(bus=1) as sensor:
        sensor.enable_gesture()

        while True:
            if sensor.gesture_available():
                gesture = sensor.read_gesture()
                name = sensor.gesture_name(gesture)
                if name != "NONE":
                    print(f"Geste erkannt: {name}")

            time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
