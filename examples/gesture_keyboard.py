#!/usr/bin/env python3
"""Gestengesteuerte Tastenkombinationen für Raspberry Pi 5.

Nutzt den APDS9960 Gestensensor um Tastatureingaben auszulösen.
Interrupt-gesteuert über gpiod – keine Gesten gehen verloren.
Läuft als Hintergrundprozess, unabhängig von X11/Wayland.

Gesten-Zuordnung:
    Rechts  -> Strg + Tab
    Links   -> Strg + 9
    Hoch    -> F11
    Runter  -> F11

Verkabelung:
    APDS9960 INT -> GPIO 4 (Pin 7) am Raspberry Pi

Benötigt Root-Rechte (für die keyboard-Bibliothek):
    sudo pip install keyboard smbus2 gpiod
    sudo python3 gesture_keyboard.py

Als Hintergrundprozess starten:
    sudo nohup python3 gesture_keyboard.py > /dev/null 2>&1 &
"""

import time
import keyboard
import gpiod
from apds9960 import APDS9960
from apds9960.registers import (
    GESTURE_RIGHT,
    GESTURE_LEFT,
    GESTURE_UP,
    GESTURE_DOWN,
    GESTURE_NONE,
    LED_BOOST_300,
)

# --- Konfiguration ---
I2C_BUS = 1
GPIO_CHIP = "/dev/gpiochip4"  # RPi 5 (bei RPi 4: /dev/gpiochip0)
GPIO_INT_PIN = 4               # GPIO-Pin für INT-Leitung des APDS9960
GESTURE_ENTRY_THRESHOLD = 30   # Niedriger = empfindlicher (Standard: 40)
GESTURE_EXIT_THRESHOLD = 20    # Niedriger = mehr Daten gesammelt (Standard: 30)


def main():
    print("Gestengesteuerte Tastenkombinationen (Interrupt-Modus)")
    print("=" * 55)
    print("Rechts -> Strg + Tab")
    print("Links  -> Strg + 9")
    print("Hoch   -> F11")
    print("Runter -> F11")
    print("=" * 55)

    sensor = APDS9960(bus=I2C_BUS)

    # Empfindlichkeit optimieren
    sensor.set_gesture_thresholds(enter=GESTURE_ENTRY_THRESHOLD,
                                  exit=GESTURE_EXIT_THRESHOLD)
    sensor.set_led_boost(LED_BOOST_300)  # Stärkeres IR-Signal

    # Gestenerkennung mit Interrupt aktivieren
    sensor.enable_gesture(interrupt=True)

    # gpiod: Interrupt-Pin konfigurieren (INT ist active-low)
    request = gpiod.request_lines(
        GPIO_CHIP,
        consumer="apds9960-gesture",
        config={GPIO_INT_PIN: gpiod.LineSettings(
            direction=gpiod.Direction.INPUT,
            edge_detection=gpiod.Edge.FALLING,
            bias=gpiod.Bias.PULL_UP,
        )},
    )

    print(f"Bereit. Warte auf Gesten (INT auf GPIO {GPIO_INT_PIN})...")
    print("Drücke Ctrl+C zum Beenden.\n")

    try:
        while True:
            # Blockiert bis der Sensor einen Interrupt auslöst (oder Timeout)
            if request.wait_edge_events(timeout=5.0):
                request.read_edge_events()  # Events konsumieren

                # FIFO auslesen bis keine Daten mehr da sind
                while sensor.gesture_available():
                    gesture = sensor.read_gesture()

                    if gesture == GESTURE_RIGHT:
                        print("-> Rechts: Strg + Tab")
                        keyboard.press_and_release("ctrl+tab")

                    elif gesture == GESTURE_LEFT:
                        print("<- Links: Strg + 9")
                        keyboard.press_and_release("ctrl+9")

                    elif gesture == GESTURE_UP:
                        print("↑  Hoch: F11")
                        keyboard.press_and_release("f11")

                    elif gesture == GESTURE_DOWN:
                        print("↓  Runter: F11")
                        keyboard.press_and_release("f11")

                sensor.clear_interrupts()

            # Kurze Pause um CPU-Last niedrig zu halten
            time.sleep(0.01)
    finally:
        request.release()
        sensor.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
