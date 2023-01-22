from interface.Interface import Interface
from PIL import Image
import config
from driver.ILI9486 import ILI9486, Origin
import RPi.GPIO as GPIO
from spidev import SpiDev


class ILI9486Interface(Interface):

    def __init__(self, flip_display: bool = False):
        GPIO.setmode(GPIO.BCM)
        spi = SpiDev(config.DISPLAY_CONFIG.bus, config.DISPLAY_CONFIG.device)
        spi.mode = 0b10  # [CPOL|CPHA] -> polarity 1, phase 0
        spi.max_speed_hz = 64000000
        origin = Origin.LOWER_RIGHT if flip_display else Origin.UPPER_LEFT
        lcd = ILI9486(dc=config.DC_PIN, rst=config.RST_PIN, spi=spi, origin=origin).begin()
        self.__spi = spi
        self.__display = lcd
        self.__blocked = False  # Flag to block new draw calls while still drawing (takes around 333 ms)

    def close(self):
        self.__display.reset()
        self.__spi.close()
        GPIO.cleanup()

    def show(self, image: Image):
        if not self.__blocked:
            self.__blocked = True
            self.__display.display(image)
            self.__blocked = False

    def show_partial(self, image: Image, x0, y0):
        if not self.__blocked:
            self.__blocked = True
            self.__display.display_partial(image, x0, y0)
            self.__blocked = False
