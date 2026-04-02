"""APDS9960 sensor driver for Raspberry Pi 5 (and older models).

Uses smbus2 for I2C communication and gpiod for optional interrupt support,
replacing the RPi.GPIO dependency that is incompatible with Raspberry Pi 5.
"""

from apds9960.device import APDS9960  # noqa: F401

__version__ = "1.0.0"
