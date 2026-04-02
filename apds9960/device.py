"""APDS9960 I2C driver for Raspberry Pi 5 (and older models).

Uses smbus2 for I2C and gpiod for optional interrupt handling,
replacing RPi.GPIO which is not available on Raspberry Pi 5.
"""

import time
from collections import namedtuple

from smbus2 import SMBus

from apds9960.registers import (
    DEVICE_ADDRESS,
    DEVICE_ID,
    REG_ENABLE,
    REG_ATIME,
    REG_WTIME,
    REG_AILTL,
    REG_AIHTL,
    REG_PILT,
    REG_PIHT,
    REG_PERS,
    REG_CONFIG1,
    REG_PPULSE,
    REG_CONTROL,
    REG_CONFIG2,
    REG_ID,
    REG_STATUS,
    REG_CDATAL,
    REG_RDATAL,
    REG_GDATAL,
    REG_BDATAL,
    REG_PDATA,
    REG_POFFSET_UR,
    REG_POFFSET_DL,
    REG_CONFIG3,
    REG_GPENTH,
    REG_GPEXTH,
    REG_GCONF1,
    REG_GCONF2,
    REG_GOFFSET_U,
    REG_GOFFSET_D,
    REG_GOFFSET_L,
    REG_GOFFSET_R,
    REG_GPULSE,
    REG_GCONF3,
    REG_GCONF4,
    REG_GFLVL,
    REG_GSTATUS,
    REG_AICLEAR,
    REG_GFIFO_U,
    BIT_GEN,
    BIT_PIEN,
    BIT_AIEN,
    BIT_WEN,
    BIT_PEN,
    BIT_AEN,
    BIT_PON,
    BIT_PVALID,
    BIT_AVALID,
    BIT_GVALID,
    BIT_GFIFO_CLR,
    BIT_GMODE,
    GESTURE_NONE,
    GESTURE_UP,
    GESTURE_DOWN,
    GESTURE_LEFT,
    GESTURE_RIGHT,
    GESTURE_NEAR,
    GESTURE_FAR,
    GESTURE_NAMES,
    DEFAULT_ATIME,
    DEFAULT_WTIME,
    DEFAULT_PPULSE,
    DEFAULT_POFFSET_UR,
    DEFAULT_POFFSET_DL,
    DEFAULT_CONFIG1,
    DEFAULT_LDRIVE,
    DEFAULT_PGAIN,
    DEFAULT_AGAIN,
    DEFAULT_PILT,
    DEFAULT_PIHT,
    DEFAULT_AILT,
    DEFAULT_AIHT,
    DEFAULT_PERS,
    DEFAULT_CONFIG2,
    DEFAULT_CONFIG3,
    DEFAULT_GPENTH,
    DEFAULT_GPEXTH,
    DEFAULT_GCONF1,
    DEFAULT_GCONF2,
    DEFAULT_GPULSE,
    DEFAULT_GOFFSET,
    DEFAULT_GCONF3,
    DEFAULT_GCONF4,
)

ColorData = namedtuple("ColorData", ["clear", "red", "green", "blue"])
GestureData = namedtuple("GestureData", ["up", "down", "left", "right"])


class APDS9960:
    """APDS9960 gesture/proximity/ALS/color sensor driver.

    Compatible with Raspberry Pi 5 and older models.
    Uses smbus2 for I2C communication (no RPi.GPIO dependency).

    Args:
        bus: I2C bus number (default: 1).
        address: I2C device address (default: 0x39).
    """

    # Gesture processing parameters
    GESTURE_THRESHOLD = 30
    GESTURE_SENSITIVITY = 20

    def __init__(self, bus=1, address=DEVICE_ADDRESS):
        self._address = address
        self._bus = SMBus(bus)
        self._gesture_ud_delta = 0
        self._gesture_lr_delta = 0
        self._gesture_ud_count = 0
        self._gesture_lr_count = 0
        self._gesture_near_count = 0
        self._gesture_far_count = 0

        # Verify device ID
        device_id = self._read_byte(REG_ID)
        if device_id != DEVICE_ID:
            raise RuntimeError(
                f"APDS9960 not found. Expected ID 0x{DEVICE_ID:02X}, "
                f"got 0x{device_id:02X}"
            )

        # Initialize with default settings
        self._init_device()

    def _init_device(self):
        """Set all registers to sensible defaults."""
        # Disable everything first
        self.enable(power=False)

        self._write_byte(REG_ATIME, DEFAULT_ATIME)
        self._write_byte(REG_WTIME, DEFAULT_WTIME)
        self._write_byte(REG_PPULSE, DEFAULT_PPULSE)
        self._write_byte(REG_POFFSET_UR, DEFAULT_POFFSET_UR)
        self._write_byte(REG_POFFSET_DL, DEFAULT_POFFSET_DL)
        self._write_byte(REG_CONFIG1, DEFAULT_CONFIG1)
        self.set_led_drive(DEFAULT_LDRIVE)
        self.set_proximity_gain(DEFAULT_PGAIN)
        self.set_als_gain(DEFAULT_AGAIN)
        self._write_byte(REG_PILT, DEFAULT_PILT)
        self._write_byte(REG_PIHT, DEFAULT_PIHT)
        self._write_word(REG_AILTL, DEFAULT_AILT)
        self._write_word(REG_AIHTL, DEFAULT_AIHT)
        self._write_byte(REG_PERS, DEFAULT_PERS)
        self._write_byte(REG_CONFIG2, DEFAULT_CONFIG2)
        self._write_byte(REG_CONFIG3, DEFAULT_CONFIG3)
        self._write_byte(REG_GPENTH, DEFAULT_GPENTH)
        self._write_byte(REG_GPEXTH, DEFAULT_GPEXTH)
        self._write_byte(REG_GCONF1, DEFAULT_GCONF1)
        self._write_byte(REG_GCONF2, DEFAULT_GCONF2)
        self._write_byte(REG_GOFFSET_U, DEFAULT_GOFFSET)
        self._write_byte(REG_GOFFSET_D, DEFAULT_GOFFSET)
        self._write_byte(REG_GOFFSET_L, DEFAULT_GOFFSET)
        self._write_byte(REG_GOFFSET_R, DEFAULT_GOFFSET)
        self._write_byte(REG_GPULSE, DEFAULT_GPULSE)
        self._write_byte(REG_GCONF3, DEFAULT_GCONF3)
        self._write_byte(REG_GCONF4, DEFAULT_GCONF4)

        # Power on
        self.enable(power=True)

    # -------------------------------------------------------------------------
    # I2C primitives
    # -------------------------------------------------------------------------
    def _read_byte(self, reg):
        return self._bus.read_byte_data(self._address, reg)

    def _write_byte(self, reg, value):
        self._bus.write_byte_data(self._address, reg, value & 0xFF)

    def _read_word(self, reg):
        low = self._bus.read_byte_data(self._address, reg)
        high = self._bus.read_byte_data(self._address, reg + 1)
        return (high << 8) | low

    def _write_word(self, reg, value):
        self._bus.write_byte_data(self._address, reg, value & 0xFF)
        self._bus.write_byte_data(self._address, reg + 1, (value >> 8) & 0xFF)

    def _read_block(self, reg, length):
        """Read a block of bytes. Uses individual reads for compatibility."""
        return [self._bus.read_byte_data(self._address, reg + i) for i in range(length)]

    def _set_bits(self, reg, mask):
        val = self._read_byte(reg)
        self._write_byte(reg, val | mask)

    def _clear_bits(self, reg, mask):
        val = self._read_byte(reg)
        self._write_byte(reg, val & ~mask)

    # -------------------------------------------------------------------------
    # Enable / disable
    # -------------------------------------------------------------------------
    def enable(self, power=True, wait=False, proximity=False, als=False,
               gesture=False, proximity_int=False, als_int=False):
        """Enable or disable sensor functions."""
        val = 0
        if power:
            val |= BIT_PON
        if wait:
            val |= BIT_WEN
        if proximity:
            val |= BIT_PEN
        if als:
            val |= BIT_AEN
        if gesture:
            val |= BIT_GEN
        if proximity_int:
            val |= BIT_PIEN
        if als_int:
            val |= BIT_AIEN
        self._write_byte(REG_ENABLE, val)

    def enable_proximity(self, interrupt=False):
        """Enable proximity detection."""
        self.enable(power=True, proximity=True, proximity_int=interrupt)

    def enable_als(self, interrupt=False):
        """Enable ambient light / color sensing."""
        self.enable(power=True, als=True, als_int=interrupt)

    def enable_gesture(self):
        """Enable gesture detection."""
        # Reset gesture FIFO
        self._set_bits(REG_GCONF4, BIT_GFIFO_CLR)
        time.sleep(0.01)
        self._clear_bits(REG_GCONF4, BIT_GFIFO_CLR)

        self.enable(power=True, wait=True, proximity=True, gesture=True)

    def disable(self):
        """Disable all sensor functions and power off."""
        self.enable(power=False)

    # -------------------------------------------------------------------------
    # Proximity
    # -------------------------------------------------------------------------
    def read_proximity(self):
        """Read proximity value (0-255). Higher = closer.

        Returns:
            int: Proximity value.
        """
        return self._read_byte(REG_PDATA)

    def proximity_available(self):
        """Check if a new proximity reading is available."""
        return bool(self._read_byte(REG_STATUS) & BIT_PVALID)

    # -------------------------------------------------------------------------
    # ALS / Color
    # -------------------------------------------------------------------------
    def read_color(self):
        """Read ambient light / color data (RGBC).

        Returns:
            ColorData: Named tuple with clear, red, green, blue values (0-65535).
        """
        clear = self._read_word(REG_CDATAL)
        red = self._read_word(REG_RDATAL)
        green = self._read_word(REG_GDATAL)
        blue = self._read_word(REG_BDATAL)
        return ColorData(clear=clear, red=red, green=green, blue=blue)

    def als_available(self):
        """Check if a new ALS/color reading is available."""
        return bool(self._read_byte(REG_STATUS) & BIT_AVALID)

    def read_ambient_light(self):
        """Read clear channel value (ambient light intensity).

        Returns:
            int: Clear channel value (0-65535).
        """
        return self._read_word(REG_CDATAL)

    # -------------------------------------------------------------------------
    # Gesture detection
    # -------------------------------------------------------------------------
    def gesture_available(self):
        """Check if gesture data is available in FIFO."""
        status = self._read_byte(REG_GSTATUS)
        return bool(status & BIT_GVALID)

    def read_gesture(self):
        """Read and decode a gesture from the FIFO.

        Call this after gesture_available() returns True.
        Processes all available FIFO data and returns the detected gesture.

        Returns:
            int: One of GESTURE_NONE, GESTURE_UP, GESTURE_DOWN,
                 GESTURE_LEFT, GESTURE_RIGHT, GESTURE_NEAR, GESTURE_FAR.
        """
        fifo_data = []

        # Collect FIFO data
        for _ in range(32):  # Max 32 datasets in FIFO
            if not self.gesture_available():
                break

            fifo_level = self._read_byte(REG_GFLVL)
            if fifo_level == 0:
                break

            for _ in range(fifo_level):
                data = self._read_block(REG_GFIFO_U, 4)
                # Only use valid readings (not saturated)
                if any(d > 0 for d in data):
                    fifo_data.append(GestureData(
                        up=data[0], down=data[1],
                        left=data[2], right=data[3]
                    ))

            time.sleep(0.03)

        if len(fifo_data) < 4:
            return GESTURE_NONE

        return self._decode_gesture(fifo_data)

    def _decode_gesture(self, data):
        """Decode gesture from FIFO data using delta analysis."""
        # Calculate ratios for first and last valid samples
        ud_first = 0
        lr_first = 0
        ud_last = 0
        lr_last = 0

        # Find first valid data point
        for sample in data:
            if (sample.up > self.GESTURE_THRESHOLD and
                    sample.down > self.GESTURE_THRESHOLD and
                    sample.left > self.GESTURE_THRESHOLD and
                    sample.right > self.GESTURE_THRESHOLD):
                ud_first = sample.up - sample.down
                lr_first = sample.left - sample.right
                break

        # Find last valid data point
        for sample in reversed(data):
            if (sample.up > self.GESTURE_THRESHOLD and
                    sample.down > self.GESTURE_THRESHOLD and
                    sample.left > self.GESTURE_THRESHOLD and
                    sample.right > self.GESTURE_THRESHOLD):
                ud_last = sample.up - sample.down
                lr_last = sample.left - sample.right
                break

        # Calculate deltas
        ud_delta = ud_last - ud_first
        lr_delta = lr_last - lr_first

        # Accumulate deltas
        self._gesture_ud_delta += ud_delta
        self._gesture_lr_delta += lr_delta

        # Determine gesture direction
        if abs(self._gesture_ud_delta) > abs(self._gesture_lr_delta):
            if abs(self._gesture_ud_delta) > self.GESTURE_SENSITIVITY:
                if self._gesture_ud_delta < 0:
                    gesture = GESTURE_UP
                else:
                    gesture = GESTURE_DOWN
            else:
                gesture = GESTURE_NONE
        else:
            if abs(self._gesture_lr_delta) > self.GESTURE_SENSITIVITY:
                if self._gesture_lr_delta < 0:
                    gesture = GESTURE_LEFT
                else:
                    gesture = GESTURE_RIGHT
            else:
                gesture = GESTURE_NONE

        # Check for near/far gestures
        if gesture == GESTURE_NONE:
            total_first = sum(data[0])
            total_last = sum(data[-1])
            if total_first > 200 and total_last < 100:
                gesture = GESTURE_FAR
            elif total_first < 100 and total_last > 200:
                gesture = GESTURE_NEAR

        # Reset accumulators
        self._gesture_ud_delta = 0
        self._gesture_lr_delta = 0

        return gesture

    @staticmethod
    def gesture_name(gesture):
        """Convert gesture constant to readable string."""
        return GESTURE_NAMES.get(gesture, "UNKNOWN")

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    def set_led_drive(self, drive):
        """Set LED drive strength (0=100mA, 1=50mA, 2=25mA, 3=12.5mA)."""
        val = self._read_byte(REG_CONTROL)
        val = (val & 0x3F) | ((drive & 0x03) << 6)
        self._write_byte(REG_CONTROL, val)

    def set_proximity_gain(self, gain):
        """Set proximity gain (0=1x, 1=2x, 2=4x, 3=8x)."""
        val = self._read_byte(REG_CONTROL)
        val = (val & 0xF3) | ((gain & 0x03) << 2)
        self._write_byte(REG_CONTROL, val)

    def set_als_gain(self, gain):
        """Set ALS gain (0=1x, 1=4x, 2=16x, 3=64x)."""
        val = self._read_byte(REG_CONTROL)
        val = (val & 0xFC) | (gain & 0x03)
        self._write_byte(REG_CONTROL, val)

    def set_gesture_gain(self, gain):
        """Set gesture gain (0=1x, 1=2x, 2=4x, 3=8x)."""
        val = self._read_byte(REG_GCONF2)
        val = (val & 0x9F) | ((gain & 0x03) << 5)
        self._write_byte(REG_GCONF2, val)

    def set_gesture_thresholds(self, enter=40, exit=30):
        """Set gesture proximity entry/exit thresholds."""
        self._write_byte(REG_GPENTH, enter)
        self._write_byte(REG_GPEXTH, exit)

    def set_proximity_thresholds(self, low=0, high=50):
        """Set proximity interrupt thresholds."""
        self._write_byte(REG_PILT, low)
        self._write_byte(REG_PIHT, high)

    def set_led_boost(self, boost):
        """Set LED boost (0=100%, 1=150%, 2=200%, 3=300%)."""
        val = self._read_byte(REG_CONFIG2)
        val = (val & 0xCF) | ((boost & 0x03) << 4)
        self._write_byte(REG_CONFIG2, val)

    def set_integration_time(self, time_ms):
        """Set ALS integration time in milliseconds (2.78ms - 712ms)."""
        atime = max(0, min(255, int(256 - time_ms / 2.78)))
        self._write_byte(REG_ATIME, atime)

    def clear_interrupts(self):
        """Clear all non-gesture interrupts."""
        self._bus.read_byte_data(self._address, REG_AICLEAR)

    # -------------------------------------------------------------------------
    # Context manager / cleanup
    # -------------------------------------------------------------------------
    def close(self):
        """Disable sensor and close I2C bus."""
        self.disable()
        self._bus.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
