#!/usr/bin/env python3
"""Gestengesteuerte Tastenkombinationen für Raspberry Pi 5.

Nutzt den APDS9960 Gestensensor um Tastatureingaben auszulösen.
Läuft als Hintergrundprozess und funktioniert unabhängig von X11/Wayland.

Gesten-Zuordnung:
    Rechts  -> Strg + Tab
    Links   -> Strg + 9
    Hoch    -> F11
    Runter  -> F11

Benötigt Root-Rechte (für die keyboard-Bibliothek):
    sudo pip install keyboard smbus2
    sudo python3 gesture_keyboard.py

Als Hintergrundprozess starten:
    sudo python3 gesture_keyboard.py &
    # oder mit nohup:
    sudo nohup python3 gesture_keyboard.py > /dev/null 2>&1 &
"""

import time
import keyboard
from apds9960 import APDS9960
from apds9960.registers import (
    GESTURE_RIGHT,
    GESTURE_LEFT,
    GESTURE_UP,
    GESTURE_DOWN,
)


def main():
    print("Gestengesteuerte Tastenkombinationen")
    print("=" * 40)
    print("Rechts -> Strg + Tab")
    print("Links  -> Strg + 9")
    print("Hoch   -> F11")
    print("Runter -> F11")
    print("=" * 40)
    print("Läuft... Drücke Ctrl+C zum Beenden.\n")

    with APDS9960(bus=1) as sensor:
        sensor.enable_gesture()

        while True:
            if sensor.gesture_available():
                gesture = sensor.read_gesture()

                if gesture == GESTURE_RIGHT:
                    print("-> Rechts: Strg + Tab")
                    keyboard.press_and_release("ctrl+tab")

                elif gesture == GESTURE_LEFT:
                    print("<- Links: Strg + 9")
                    keyboard.press_and_release("ctrl+9")

                elif gesture in (GESTURE_UP, GESTURE_DOWN):
                    direction = "Hoch" if gesture == GESTURE_UP else "Runter"
                    print(f"{'↑' if gesture == GESTURE_UP else '↓'} {direction}: F11")
                    keyboard.press_and_release("f11")

            time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
