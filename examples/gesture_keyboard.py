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
    LED_BOOST_300,
)

# --- Konfiguration ---
I2C_BUS = 1
GPIO_CHIP = "/dev/gpiochip4"  # RPi 5 (bei RPi 4: /dev/gpiochip0)
GPIO_INT_PIN = 4               # GPIO-Pin für INT-Leitung des APDS9960
GESTURE_ENTRY_THRESHOLD = 30   # Niedriger = empfindlicher (Standard: 40)
GESTURE_EXIT_THRESHOLD = 20    # Niedriger = mehr Daten gesammelt (Standard: 30)

# gpiod v1.x vs v2.x haben komplett unterschiedliche APIs
_GPIOD_V2 = hasattr(gpiod, "request_lines")

if _GPIOD_V2:
    from gpiod.line import Direction, Edge, Bias


def _setup_interrupt_v2():
    """Interrupt mit gpiod v2.x API einrichten."""
    request = gpiod.request_lines(
        GPIO_CHIP,
        consumer="apds9960-gesture",
        config={GPIO_INT_PIN: gpiod.LineSettings(
            direction=Direction.INPUT,
            edge_detection=Edge.FALLING,
            bias=Bias.PULL_UP,
        )},
    )
    return request


def _wait_for_interrupt_v2(request, timeout=5.0):
    """Auf Interrupt warten (gpiod v2.x)."""
    if request.wait_edge_events(timeout=timeout):
        request.read_edge_events()
        return True
    return False


def _cleanup_v2(request):
    """Aufräumen (gpiod v2.x)."""
    request.release()


def _setup_interrupt_v1():
    """Interrupt mit gpiod v1.x API einrichten."""
    chip = gpiod.Chip(GPIO_CHIP)
    line = chip.get_line(GPIO_INT_PIN)
    line.request(
        consumer="apds9960-gesture",
        type=gpiod.LINE_REQ_EV_FALLING_EDGE,
        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
    )
    return (chip, line)


def _wait_for_interrupt_v1(handle, timeout=5.0):
    """Auf Interrupt warten (gpiod v1.x)."""
    _chip, line = handle
    if line.event_wait(sec=int(timeout), nsec=int((timeout % 1) * 1e9)):
        line.event_read()
        return True
    return False


def _cleanup_v1(handle):
    """Aufräumen (gpiod v1.x)."""
    chip, line = handle
    line.release()
    chip.close()


def main():
    print("Gestengesteuerte Tastenkombinationen (Interrupt-Modus)")
    print("=" * 55)
    print("Rechts -> Strg + Tab")
    print("Links  -> Strg + 9")
    print("Hoch   -> F11")
    print("Runter -> F11")
    print("=" * 55)

    if _GPIOD_V2:
        print(f"gpiod API: v2.x")
        setup_int = _setup_interrupt_v2
        wait_int = _wait_for_interrupt_v2
        cleanup_int = _cleanup_v2
    else:
        print(f"gpiod API: v1.x")
        setup_int = _setup_interrupt_v1
        wait_int = _wait_for_interrupt_v1
        cleanup_int = _cleanup_v1

    sensor = APDS9960(bus=I2C_BUS)

    # Empfindlichkeit optimieren
    sensor.set_gesture_thresholds(enter=GESTURE_ENTRY_THRESHOLD,
                                  exit=GESTURE_EXIT_THRESHOLD)
    sensor.set_led_boost(LED_BOOST_300)  # Stärkeres IR-Signal

    # Gestenerkennung mit Interrupt aktivieren
    sensor.enable_gesture(interrupt=True)

    # gpiod: Interrupt-Pin konfigurieren (INT ist active-low)
    handle = setup_int()

    print(f"Bereit. Warte auf Gesten (INT auf GPIO {GPIO_INT_PIN})...")
    print("Drücke Ctrl+C zum Beenden.\n")

    try:
        while True:
            # Blockiert bis der Sensor einen Interrupt auslöst (oder Timeout)
            if wait_int(handle):
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

            time.sleep(0.01)
    finally:
        cleanup_int(handle)
        sensor.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
