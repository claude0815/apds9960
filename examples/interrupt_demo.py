#!/usr/bin/env python3
"""Interrupt-based proximity demo using gpiod (Raspberry Pi 5 compatible).

This demo shows how to use hardware interrupts with gpiod instead of RPi.GPIO.
Connect the APDS9960 INT pin to a GPIO pin (default: GPIO 4 / Pin 7).

Supports both gpiod v1.x and v2.x APIs.

Additional dependency:
    pip install gpiod

Wiring:
    APDS9960 INT  ->  GPIO 4 (Pin 7)
"""

import gpiod
from apds9960 import APDS9960

# Configuration
GPIO_CHIP = "/dev/gpiochip4"  # RPi 5 uses gpiochip4
GPIO_LINE = 4                  # GPIO pin number for INT
PROXIMITY_THRESHOLD = 50

_GPIOD_V2 = hasattr(gpiod, "request_lines")


def main():
    print("APDS9960 Interrupt Demo (gpiod)")
    print("=" * 40)
    print(f"Warte auf Proximity-Interrupts (Schwelle: {PROXIMITY_THRESHOLD})...")
    print("Drücke Ctrl+C zum Beenden.\n")

    sensor = APDS9960(bus=1)

    # Configure proximity interrupt
    sensor.set_proximity_thresholds(low=0, high=PROXIMITY_THRESHOLD)
    sensor.enable_proximity(interrupt=True)

    if _GPIOD_V2:
        # gpiod v2.x API
        request = gpiod.request_lines(
            GPIO_CHIP,
            consumer="apds9960-int",
            config={GPIO_LINE: gpiod.LineSettings(
                direction=gpiod.Direction.INPUT,
                edge_detection=gpiod.Edge.FALLING,
                bias=gpiod.Bias.PULL_UP,
            )},
        )
        try:
            while True:
                if request.wait_edge_events(timeout=5.0):
                    request.read_edge_events()
                    proximity = sensor.read_proximity()
                    print(f"Interrupt! Proximity: {proximity}")
                    sensor.clear_interrupts()
        finally:
            request.release()
            sensor.close()
    else:
        # gpiod v1.x API
        chip = gpiod.Chip(GPIO_CHIP)
        line = chip.get_line(GPIO_LINE)
        line.request(
            consumer="apds9960-int",
            type=gpiod.LINE_REQ_EV_FALLING_EDGE,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
        )
        try:
            while True:
                if line.event_wait(sec=5):
                    line.event_read()
                    proximity = sensor.read_proximity()
                    print(f"Interrupt! Proximity: {proximity}")
                    sensor.clear_interrupts()
        finally:
            line.release()
            chip.close()
            sensor.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
