#!/usr/bin/env python3
"""Proximity detection demo for APDS9960 on Raspberry Pi 5."""

import time
from apds9960 import APDS9960


def main():
    print("APDS9960 Proximity Demo")
    print("=" * 40)
    print("Bewege deine Hand näher/weiter vom Sensor...")
    print("Drücke Ctrl+C zum Beenden.\n")

    with APDS9960(bus=1) as sensor:
        sensor.enable_proximity()

        while True:
            if sensor.proximity_available():
                value = sensor.read_proximity()
                bar = "#" * (value // 5)
                print(f"Proximity: {value:3d}  |{bar}")

            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
