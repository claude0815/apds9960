"""APDS9960 register definitions and constants."""

# I2C address
DEVICE_ADDRESS = 0x39
DEVICE_ID = 0xAB  # Expected value in ID register

# -----------------------------------------------------------------------------
# Register addresses
# -----------------------------------------------------------------------------
REG_ENABLE = 0x80
REG_ATIME = 0x81      # ALS ADC integration time
REG_WTIME = 0x83      # Wait time
REG_AILTL = 0x84      # ALS interrupt low threshold, low byte
REG_AILTH = 0x85      # ALS interrupt low threshold, high byte
REG_AIHTL = 0x86      # ALS interrupt high threshold, low byte
REG_AIHTH = 0x87      # ALS interrupt high threshold, high byte
REG_PILT = 0x89       # Proximity interrupt low threshold
REG_PIHT = 0x8B       # Proximity interrupt high threshold
REG_PERS = 0x8C       # Interrupt persistence filters
REG_CONFIG1 = 0x8D    # Configuration register one
REG_PPULSE = 0x8E     # Proximity pulse count and length
REG_CONTROL = 0x8F    # Gain control
REG_CONFIG2 = 0x90    # Configuration register two
REG_ID = 0x92         # Device ID
REG_STATUS = 0x93     # Device status
REG_CDATAL = 0x94     # Clear/IR channel low data
REG_CDATAH = 0x95     # Clear/IR channel high data
REG_RDATAL = 0x96     # Red channel low data
REG_RDATAH = 0x97     # Red channel high data
REG_GDATAL = 0x98     # Green channel low data
REG_GDATAH = 0x99     # Green channel high data
REG_BDATAL = 0x9A     # Blue channel low data
REG_BDATAH = 0x9B     # Blue channel high data
REG_PDATA = 0x9C      # Proximity data
REG_POFFSET_UR = 0x9D # Proximity offset UP/RIGHT
REG_POFFSET_DL = 0x9E # Proximity offset DOWN/LEFT
REG_CONFIG3 = 0x9F    # Configuration register three
REG_GPENTH = 0xA0     # Gesture proximity entry threshold
REG_GPEXTH = 0xA1     # Gesture proximity exit threshold
REG_GCONF1 = 0xA2     # Gesture configuration one
REG_GCONF2 = 0xA3     # Gesture configuration two
REG_GOFFSET_U = 0xA4  # Gesture offset UP
REG_GOFFSET_D = 0xA5  # Gesture offset DOWN
REG_GOFFSET_L = 0xA7  # Gesture offset LEFT
REG_GOFFSET_R = 0xA9  # Gesture offset RIGHT
REG_GPULSE = 0xA6     # Gesture pulse count and length
REG_GCONF3 = 0xAA     # Gesture configuration three
REG_GCONF4 = 0xAB     # Gesture configuration four
REG_GFLVL = 0xAE      # Gesture FIFO level
REG_GSTATUS = 0xAF    # Gesture status
REG_IFORCE = 0xE4     # Force interrupt
REG_PICLEAR = 0xE5    # Proximity interrupt clear
REG_CICLEAR = 0xE6    # ALS clear channel interrupt clear
REG_AICLEAR = 0xE7    # All non-gesture interrupts clear
REG_GFIFO_U = 0xFC    # Gesture FIFO UP value
REG_GFIFO_D = 0xFD    # Gesture FIFO DOWN value
REG_GFIFO_L = 0xFE    # Gesture FIFO LEFT value
REG_GFIFO_R = 0xFF    # Gesture FIFO RIGHT value

# -----------------------------------------------------------------------------
# ENABLE register bits (0x80)
# -----------------------------------------------------------------------------
BIT_GEN = 0x40   # Gesture enable
BIT_PIEN = 0x20  # Proximity interrupt enable
BIT_AIEN = 0x10  # ALS interrupt enable
BIT_WEN = 0x08   # Wait enable
BIT_PEN = 0x04   # Proximity detect enable
BIT_AEN = 0x02   # ALS enable
BIT_PON = 0x01   # Power ON

# -----------------------------------------------------------------------------
# STATUS register bits (0x93)
# -----------------------------------------------------------------------------
BIT_CPSAT = 0x80  # Clear photodiode saturation
BIT_PGSAT = 0x40  # Proximity saturation (analog)
BIT_PINT = 0x20   # Proximity interrupt
BIT_AINT = 0x10   # ALS interrupt
BIT_GINT = 0x04   # Gesture interrupt
BIT_PVALID = 0x02 # Proximity valid
BIT_AVALID = 0x01 # ALS valid

# -----------------------------------------------------------------------------
# GSTATUS register bits (0xAF)
# -----------------------------------------------------------------------------
BIT_GFOV = 0x02  # Gesture FIFO overflow
BIT_GVALID = 0x01  # Gesture FIFO data valid

# -----------------------------------------------------------------------------
# GCONF4 register bits (0xAB)
# -----------------------------------------------------------------------------
BIT_GFIFO_CLR = 0x04  # Clear gesture FIFO
BIT_GIEN = 0x02       # Gesture interrupt enable
BIT_GMODE = 0x01      # Gesture mode

# -----------------------------------------------------------------------------
# Default configuration values
# -----------------------------------------------------------------------------
DEFAULT_ATIME = 219       # 103ms integration time
DEFAULT_WTIME = 246       # 27ms wait time
DEFAULT_PPULSE = 0x00     # 4us, 1 pulse (minimum)
DEFAULT_POFFSET_UR = 0
DEFAULT_POFFSET_DL = 0
DEFAULT_CONFIG1 = 0x60    # No 12x wait (WLONG = 0)
DEFAULT_LDRIVE = 3        # LED drive: 12.5mA (reduced to avoid saturation)
DEFAULT_PGAIN = 0         # Proximity gain: 1x
DEFAULT_AGAIN = 1         # ALS gain: 4x
DEFAULT_PILT = 0
DEFAULT_PIHT = 50
DEFAULT_AILT = 0xFFFF
DEFAULT_AIHT = 0
DEFAULT_PERS = 0x11       # 2 consecutive proximity or ALS for interrupt
DEFAULT_CONFIG2 = 0x01    # No saturation interrupts or LED boost
DEFAULT_CONFIG3 = 0       # Enable all photodiodes, no SAI
DEFAULT_GPENTH = 40       # Gesture entry threshold
DEFAULT_GPEXTH = 30       # Gesture exit threshold
DEFAULT_GCONF1 = 0x40     # 4 gesture events for interrupt, 1 event per fifo
DEFAULT_GCONF2 = 0x19     # Gain 1x, LED drive 12.5mA, 8us gesture wait
DEFAULT_GPULSE = 0x00     # 4us, 1 pulse (minimum)
DEFAULT_GOFFSET_U = 0     # Offsets not effective on cheap clones
DEFAULT_GOFFSET_D = 0
DEFAULT_GOFFSET_L = 0
DEFAULT_GOFFSET_R = 0
DEFAULT_GCONF3 = 0        # All photodiodes active during gesture
DEFAULT_GCONF4 = 0        # Gesture interrupts disabled, gesture mode off

# -----------------------------------------------------------------------------
# Gesture directions
# -----------------------------------------------------------------------------
GESTURE_NONE = 0
GESTURE_UP = 1
GESTURE_DOWN = 2
GESTURE_LEFT = 3
GESTURE_RIGHT = 4
GESTURE_NEAR = 5
GESTURE_FAR = 6

GESTURE_NAMES = {
    GESTURE_NONE: "NONE",
    GESTURE_UP: "UP",
    GESTURE_DOWN: "DOWN",
    GESTURE_LEFT: "LEFT",
    GESTURE_RIGHT: "RIGHT",
    GESTURE_NEAR: "NEAR",
    GESTURE_FAR: "FAR",
}

# -----------------------------------------------------------------------------
# LED drive strength
# -----------------------------------------------------------------------------
LED_DRIVE_100MA = 0
LED_DRIVE_50MA = 1
LED_DRIVE_25MA = 2
LED_DRIVE_12_5MA = 3

# Proximity gain
PGAIN_1X = 0
PGAIN_2X = 1
PGAIN_4X = 2
PGAIN_8X = 3

# ALS gain
AGAIN_1X = 0
AGAIN_4X = 1
AGAIN_16X = 2
AGAIN_64X = 3

# Gesture gain
GGAIN_1X = 0
GGAIN_2X = 1
GGAIN_4X = 2
GGAIN_8X = 3

# LED boost
LED_BOOST_100 = 0
LED_BOOST_150 = 1
LED_BOOST_200 = 2
LED_BOOST_300 = 3
