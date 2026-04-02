#!/usr/bin/env python3
"""Color/ambient light sensor demo for APDS9960 on Raspberry Pi 5."""

import time
from apds9960 import APDS9960


def main():
    print("APDS9960 Farb-/Lichtsensor Demo")
    print("=" * 40)
    print("Halte verschiedenfarbige Objekte vor den Sensor...")
    print("Drücke Ctrl+C zum Beenden.\n")

    with APDS9960(bus=1) as sensor:
        sensor.enable_als()

        while True:
            if sensor.als_available():
                color = sensor.read_color()
                print(
                    f"Clear: {color.clear:5d}  "
                    f"R: {color.red:5d}  "
                    f"G: {color.green:5d}  "
                    f"B: {color.blue:5d}"
                )

            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
