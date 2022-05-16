from PIL import ImageFont


class SpiConfig:
    """Representation of an SPI device configuration"""
    def __init__(self, bus: int, device: int):
        self.__bus = bus
        self.__device = device

    @property
    def bus(self) -> int:
        return self.__bus

    @property
    def device(self) -> int:
        return self.__device


# Interface definition (SPI display module ignores this, it supports only its own resolution)
WIDTH: int = 480
HEIGHT: int = 320
RESOLUTION = WIDTH, HEIGHT

# App definition
APP_SIDE_OFFSET: int = 20
APP_TOP_OFFSET: int = 30
APP_BOTTOM_OFFSET: int = 25

# Fonts
FONT_NAME = 'FreeSansBold.ttf'
FONT_HEADER = ImageFont.truetype(FONT_NAME, 16)
FONT_STANDARD = ImageFont.truetype(FONT_NAME, 14)

# Colors
BACKGROUND = (0, 0, 0)
ACCENT = (27, 251, 30)
ACCENT_DARK = (9, 64, 9)

# Display module definition
RST_PIN = 25
DC_PIN = 24
DISPLAY_CONFIG = SpiConfig(0, 0)

# Touch module definition
CS_PIN = 7
IRQ_PIN = 17
TOUCH_CONFIG = SpiConfig(0, 1)
