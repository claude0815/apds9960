#!/usr/bin/env python3
"""Debug-Skript: Zeigt die rohen FIFO-Daten des APDS9960 Gestensensors.

Damit lässt sich prüfen, ob die Photodioden-Zuordnung (UP/DOWN/LEFT/RIGHT)
zur physischen Orientierung des Sensors passt.

Bewege deine Hand langsam in eine Richtung und beobachte die Werte.
"""

import time
from apds9960 import APDS9960
from apds9960.registers import (
    REG_GFIFO_U, REG_GFLVL, REG_GSTATUS, BIT_GVALID,
    REG_CONTROL, REG_GCONF2, REG_PPULSE, REG_GPULSE, REG_CONFIG2,
    REG_GPENTH, REG_GPEXTH, REG_ENABLE,
    REG_GOFFSET_U, REG_GOFFSET_D, REG_GOFFSET_L, REG_GOFFSET_R,
)


def print_register_config(sensor):
    """Aktuelle Register-Werte auslesen und anzeigen."""
    enable = sensor._read_byte(REG_ENABLE)
    control = sensor._read_byte(REG_CONTROL)
    gconf2 = sensor._read_byte(REG_GCONF2)
    ppulse = sensor._read_byte(REG_PPULSE)
    gpulse = sensor._read_byte(REG_GPULSE)
    config2 = sensor._read_byte(REG_CONFIG2)
    gpenth = sensor._read_byte(REG_GPENTH)
    gpexth = sensor._read_byte(REG_GPEXTH)

    ldrive = (control >> 6) & 0x03
    pgain = (control >> 2) & 0x03
    ggain = (gconf2 >> 5) & 0x03
    gldrive = (gconf2 >> 3) & 0x03
    led_boost = (config2 >> 4) & 0x03
    pplen = (ppulse >> 6) & 0x03
    ppcount = (ppulse & 0x3F) + 1
    gplen = (gpulse >> 6) & 0x03
    gpcount = (gpulse & 0x3F) + 1

    drive_ma = {0: "100mA", 1: "50mA", 2: "25mA", 3: "12.5mA"}
    gain_names = {0: "1x", 1: "2x", 2: "4x", 3: "8x"}
    pulse_us = {0: "4µs", 1: "8µs", 2: "16µs", 3: "32µs"}
    boost_pct = {0: "100%", 1: "150%", 2: "200%", 3: "300%"}

    print("Register-Konfiguration:")
    print(f"  ENABLE:     0x{enable:02X}")
    print(f"  LED Drive:  {drive_ma[ldrive]} (CONTROL=0x{control:02X})")
    print(f"  P-Gain:     {gain_names[pgain]}")
    print(f"  G-Gain:     {gain_names[ggain]} (GCONF2=0x{gconf2:02X})")
    print(f"  G-LED:      {drive_ma[gldrive]}")
    print(f"  LED Boost:  {boost_pct[led_boost]} (CONFIG2=0x{config2:02X})")
    print(f"  P-Pulse:    {pulse_us[pplen]}, {ppcount}x (PPULSE=0x{ppulse:02X})")
    print(f"  G-Pulse:    {pulse_us[gplen]}, {gpcount}x (GPULSE=0x{gpulse:02X})")
    print(f"  G-Entry-TH: {gpenth}")
    print(f"  G-Exit-TH:  {gpexth}")

    def signed(v):
        return v - 256 if v > 127 else v

    goff_u = sensor._read_byte(REG_GOFFSET_U)
    goff_d = sensor._read_byte(REG_GOFFSET_D)
    goff_l = sensor._read_byte(REG_GOFFSET_L)
    goff_r = sensor._read_byte(REG_GOFFSET_R)
    print(f"  G-Offset:   U={signed(goff_u):+4d}  D={signed(goff_d):+4d}  "
          f"L={signed(goff_l):+4d}  R={signed(goff_r):+4d}")
    print()


def main():
    print("APDS9960 Gesten-Debug")
    print("=" * 60)

    sensor = APDS9960(bus=1)
    sensor.enable_gesture()

    print_register_config(sensor)

    print("Bewege deine Hand langsam über den Sensor.")
    print("Spalten: UP  DOWN  LEFT  RIGHT  | UD-Diff  LR-Diff")
    print("=" * 60)
    print()

    while True:
        status = sensor._read_byte(REG_GSTATUS)
        if status & BIT_GVALID:
            fifo_level = sensor._read_byte(REG_GFLVL)
            if fifo_level > 0:
                print(f"--- {fifo_level} Samples ---")
                for _ in range(fifo_level):
                    data = sensor._read_block(REG_GFIFO_U, 4)
                    u, d, l, r = data
                    ud = u - d
                    lr = l - r
                    print(f"  U:{u:3d}  D:{d:3d}  L:{l:3d}  R:{r:3d}  "
                          f"| UD:{ud:+4d}  LR:{lr:+4d}")
                print()

        time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeendet.")
