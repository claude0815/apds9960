#!/usr/bin/env python3
"""Debug-Skript: Zeigt die rohen FIFO-Daten des APDS9960 Gestensensors.

Damit lässt sich prüfen, ob die Photodioden-Zuordnung (UP/DOWN/LEFT/RIGHT)
zur physischen Orientierung des Sensors passt.

Bewege deine Hand langsam in eine Richtung und beobachte die Werte.
"""

import time
from apds9960 import APDS9960
from apds9960.registers import REG_GFIFO_U, REG_GFLVL, BIT_GVALID, REG_GSTATUS


def main():
    print("APDS9960 Gesten-Debug")
    print("=" * 60)
    print("Bewege deine Hand langsam über den Sensor.")
    print("Spalten: UP  DOWN  LEFT  RIGHT  | UD-Diff  LR-Diff")
    print("=" * 60)
    print()

    sensor = APDS9960(bus=1)
    sensor.enable_gesture()

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
