from PIL import ImageFont


# Display definition (SPI display module ignores this, it supports only its own resolution)
WIDTH = 480
HEIGHT = 320
RESOLUTION = WIDTH, HEIGHT

# Fonts
FONT_NAME = 'FreeSansBold.ttf'
FONT_HEADER = ImageFont.truetype(FONT_NAME, 16)
FONT_STANDARD = ImageFont.truetype(FONT_NAME, 14)

# Colors
BACKGROUND = (0, 0, 0)
ACCENT = (27, 251, 30)
ACCENT_DARK = (9, 64, 9)

# Pin definition
RST_PIN = 25
DC_PIN = 24
# SPI definition
SPI_BUS = 0
SPI_DEVICE = 0

# App definition
APP_SIDE_OFFSET: int = 20
APP_TOP_OFFSET: int = 30
APP_BOTTOM_OFFSET: int = 25
