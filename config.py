from PIL import ImageFont


class SPIConfig:
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


DEV_MODE = 1

# Interface definition (SPI display module ignores this, it supports only its own resolution)
WIDTH: int = 480
HEIGHT: int = 320
RESOLUTION = WIDTH, HEIGHT
# flip display by 180° (SPI display module only)
FLIP_DISPLAY = False

# App definition
APP_SIDE_OFFSET: int = 20
APP_TOP_OFFSET: int = 30
APP_BOTTOM_OFFSET: int = 25

# Fonts
FONT_NAME = 'FreeSansBold.ttf'
FONT_HEADER = ImageFont.truetype(FONT_NAME, 16)
FONT_STANDARD = ImageFont.truetype(FONT_NAME, 14)

# Colors
COLOR_MODE = 0  # 0 for standard mode, 1 for power armor mode
BACKGROUND = (0, 0, 0)
if COLOR_MODE == 0:
    ACCENT = (27, 251, 30)
    ACCENT_DARK = (9, 64, 9)
else:
    ACCENT = (255, 246, 101)
    ACCENT_DARK = (59, 45, 25)

# Display module definition
RST_PIN = 25
DC_PIN = 24
DISPLAY_CONFIG = SPIConfig(0, 0)

# Touch module definition
CS_PIN = 7
IRQ_PIN = 17
TOUCH_CONFIG = SPIConfig(0, 1)

# Buttons definition
UP_PIN = 5
DOWN_PIN = 6
LEFT_PIN = 12
RIGHT_PIN = 13
A_PIN = 16
B_PIN = 26

# Rotary encoder definition
CLK_PIN = 22
DT_PIN = 23
SW_PIN = 27  # pressing the encoder switch, unused so far
