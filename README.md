# APDS9960 - Raspberry Pi 5 kompatibel

Python-Treiber für den APDS9960 Gesten-/Näherungs-/Farb-/Lichtsensor über I2C.

**Funktioniert auf dem Raspberry Pi 5** – verwendet `smbus2` statt `RPi.GPIO`.

## Features

- Gestenerkennung (Hoch, Runter, Links, Rechts, Nah, Fern)
- Näherungserkennung (Proximity)
- Farb-/Lichtsensor (RGBC)
- Optional: Hardware-Interrupts über `gpiod` (RPi 5 kompatibel)
- Kein `RPi.GPIO` erforderlich

## Voraussetzungen

### Hardware

- Raspberry Pi (jedes Modell, einschließlich RPi 5)
- APDS9960 Breakout-Board (z.B. von Adafruit, SparkFun)
- Verkabelung:

| APDS9960 | Raspberry Pi     |
|----------|------------------|
| VIN      | 3.3V (Pin 1)    |
| GND      | GND (Pin 6)     |
| SDA      | SDA (Pin 3)     |
| SCL      | SCL (Pin 5)     |
| INT      | GPIO 4 (Pin 7)  | *(optional, nur für Interrupts)*

### Software

1. I2C aktivieren:
   ```bash
   sudo raspi-config
   # -> Interface Options -> I2C -> Enable
   ```

2. Abhängigkeiten installieren:
   ```bash
   pip install smbus2
   # Optional, für Interrupt-Unterstützung:
   pip install gpiod
   ```

## Verwendung

### Gestenerkennung

```python
from apds9960 import APDS9960
import time

with APDS9960(bus=1) as sensor:
    sensor.enable_gesture()

    while True:
        if sensor.gesture_available():
            gesture = sensor.read_gesture()
            print(sensor.gesture_name(gesture))
        time.sleep(0.05)
```

### Näherungserkennung

```python
from apds9960 import APDS9960
import time

with APDS9960(bus=1) as sensor:
    sensor.enable_proximity()

    while True:
        if sensor.proximity_available():
            print(f"Proximity: {sensor.read_proximity()}")
        time.sleep(0.1)
```

### Farbsensor

```python
from apds9960 import APDS9960
import time

with APDS9960(bus=1) as sensor:
    sensor.enable_als()

    while True:
        if sensor.als_available():
            color = sensor.read_color()
            print(f"R:{color.red} G:{color.green} B:{color.blue} C:{color.clear}")
        time.sleep(0.5)
```

### Interrupts mit gpiod (RPi 5)

```python
import gpiod
from apds9960 import APDS9960

sensor = APDS9960(bus=1)
sensor.set_proximity_thresholds(low=0, high=50)
sensor.enable_proximity(interrupt=True)

request = gpiod.request_lines(
    "/dev/gpiochip4",  # RPi 5
    consumer="apds9960",
    config={4: gpiod.LineSettings(
        direction=gpiod.Direction.INPUT,
        edge_detection=gpiod.Edge.FALLING,
        bias=gpiod.Bias.PULL_UP,
    )},
)

while True:
    if request.wait_edge_events(timeout=5.0):
        request.read_edge_events()
        print(f"Proximity: {sensor.read_proximity()}")
        sensor.clear_interrupts()
```

## Beispiele

```bash
python3 examples/gesture_demo.py     # Gestenerkennung
python3 examples/proximity_demo.py   # Näherungserkennung
python3 examples/color_demo.py       # Farbsensor
python3 examples/interrupt_demo.py   # Hardware-Interrupts (gpiod)
```

## Warum nicht RPi.GPIO?

Der Raspberry Pi 5 verwendet einen neuen RP1 GPIO-Controller. Die `RPi.GPIO`-Bibliothek
unterstützt diesen nicht. Diese Bibliothek nutzt stattdessen:

- **`smbus2`** für I2C-Kommunikation (funktioniert auf allen RPi-Modellen)
- **`gpiod`** für optionale Hardware-Interrupts (RPi 5 kompatibel)
