#!/usr/bin/env python3
"""Gestengesteuerte Tastenkombinationen für Raspberry Pi 5.

Nutzt den APDS9960 Gestensensor um Tastatureingaben auszulösen.
Hybrid-Modus: Interrupt-gesteuert wenn INT-Pin verkabelt, sonst Polling-Fallback.
Läuft als Hintergrundprozess, unabhängig von X11/Wayland.

Gesten-Zuordnung:
    Rechts  -> Strg + Tab
    Links   -> Alt + Tab
    Hoch    -> HDMI einschalten (wlopm)
    Runter  -> F5

Verkabelung (optional, für Interrupt-Modus):
    APDS9960 INT -> GPIO 4 (Pin 7) am Raspberry Pi

Benötigt Root-Rechte (für die keyboard-Bibliothek):
    sudo pip install keyboard smbus2
    sudo python3 gesture_keyboard.py

Optional für Interrupt-Modus:
    sudo pip install gpiod

Als Hintergrundprozess starten:
    sudo nohup python3 gesture_keyboard.py > /dev/null 2>&1 &
"""

import time
import subprocess
import keyboard
from apds9960 import APDS9960
from apds9960.registers import (
    GESTURE_RIGHT,
    GESTURE_LEFT,
    GESTURE_UP,
    GESTURE_DOWN,
)

# --- Konfiguration ---
I2C_BUS = 1
GPIO_CHIP = "/dev/gpiochip0"  # RPi 5: pinctrl-rp1
GPIO_INT_PIN = 4               # GPIO-Pin für INT-Leitung des APDS9960


# -------------------------------------------------------------------------
# Interrupt-Setup (optional, wird nur bei vorhandenem gpiod + INT-Pin genutzt)
# -------------------------------------------------------------------------
def _try_setup_interrupt():
    """Versuche Interrupt via gpiod einzurichten. Gibt None zurück bei Fehler."""
    try:
        import gpiod
    except ImportError:
        print("[INFO] gpiod nicht installiert -> Polling-Modus")
        return None

    try:
        if hasattr(gpiod, "request_lines"):
            # gpiod v2.x
            from gpiod.line import Direction, Edge, Bias
            handle = gpiod.request_lines(
                GPIO_CHIP,
                consumer="apds9960-gesture",
                config={GPIO_INT_PIN: gpiod.LineSettings(
                    direction=Direction.INPUT,
                    edge_detection=Edge.FALLING,
                    bias=Bias.PULL_UP,
                )},
            )
            print(f"[INFO] gpiod v2.x -> Interrupt-Modus (GPIO {GPIO_INT_PIN})")
            return ("v2", handle)
        else:
            # gpiod v1.x
            chip = gpiod.Chip(GPIO_CHIP)
            line = chip.get_line(GPIO_INT_PIN)
            line.request(
                consumer="apds9960-gesture",
                type=gpiod.LINE_REQ_EV_FALLING_EDGE,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
            print(f"[INFO] gpiod v1.x -> Interrupt-Modus (GPIO {GPIO_INT_PIN})")
            return ("v1", chip, line)
    except Exception as e:
        print(f"[WARN] Interrupt-Setup fehlgeschlagen: {e}")
        print("[INFO] Fallback -> Polling-Modus")
        return None


def _wait_for_interrupt(int_handle, timeout=0.2):
    """Warte auf Interrupt. Gibt True zurück wenn ausgelöst."""
    if int_handle[0] == "v2":
        request = int_handle[1]
        if request.wait_edge_events(timeout=timeout):
            request.read_edge_events()
            return True
    else:
        line = int_handle[2]
        if line.event_wait(sec=0, nsec=int(timeout * 1e9)):
            line.event_read()
            return True
    return False


def _cleanup_interrupt(int_handle):
    """Interrupt-Ressourcen freigeben."""
    if int_handle[0] == "v2":
        int_handle[1].release()
    else:
        int_handle[2].release()
        int_handle[1].close()


# -------------------------------------------------------------------------
# Gesten verarbeiten
# -------------------------------------------------------------------------
def handle_gesture(gesture):
    """Erkannte Geste in Tastendruck umsetzen."""
    if gesture == GESTURE_RIGHT:
        print("-> Rechts: Strg + Tab")
        keyboard.press_and_release("ctrl+tab")
    elif gesture == GESTURE_LEFT:
        print("<- Links: Alt + Tab")
        keyboard.press_and_release("alt+tab")
    elif gesture == GESTURE_UP:
        print("↑  Hoch: HDMI einschalten")
        subprocess.run(
            ["wlopm", "--on", "HDMI-A-1"],
            env={"WAYLAND_DISPLAY": "wayland-0",
                 "XDG_RUNTIME_DIR": "/run/user/1000"},
        )
    elif gesture == GESTURE_DOWN:
        print("↓  Runter: F5")
        keyboard.press_and_release("f5")


def main():
    print("Gestengesteuerte Tastenkombinationen")
    print("=" * 55)
    print("Rechts -> Strg + Tab")
    print("Links  -> Alt + Tab")
    print("Hoch   -> HDMI einschalten")
    print("Runter -> F5")
    print("=" * 55)

    sensor = APDS9960(bus=I2C_BUS)

    # Interrupt versuchen, sonst Polling
    int_handle = _try_setup_interrupt()
    use_interrupt = int_handle is not None

    # Gestenerkennung aktivieren (mit Interrupt falls verfügbar)
    sensor.enable_gesture(interrupt=use_interrupt)

    if not use_interrupt:
        print("[INFO] Polling-Modus aktiv (kein INT-Pin nötig)")

    print("Bereit. Warte auf Gesten...")
    print("Drücke Ctrl+C zum Beenden.\n")

    try:
        while True:
            if use_interrupt:
                # Hybrid: kurzer Interrupt-Wait, dann trotzdem FIFO prüfen
                _wait_for_interrupt(int_handle, timeout=0.2)

            # FIFO immer prüfen (Polling-Fallback & nach Interrupt)
            if sensor.gesture_available():
                gesture = sensor.read_gesture()
                handle_gesture(gesture)

                if use_interrupt:
                    sensor.clear_interrupts()

            time.sleep(0.05)
    finally:
        if use_interrupt:
            _cleanup_interrupt(int_handle)
        sensor.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
