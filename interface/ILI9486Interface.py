from interface.BaseInterface import BaseInterface
from PIL import Image
import config
from driver.ILI9486 import ILI9486
import RPi.GPIO as GPIO
from spidev import SpiDev


class ILI9486Interface(BaseInterface):

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        spi = SpiDev(config.DISPLAY_CONFIG.bus, config.DISPLAY_CONFIG.device)
        spi.mode = 0b10  # [CPOL|CPHA] -> polarity 1, phase 0
        spi.max_speed_hz = 64000000
        lcd = ILI9486(dc=config.DC_PIN, rst=config.RST_PIN, spi=spi).begin()
        self.__spi = spi
        self.__display = lcd

    def close(self):
        self.__display.reset()
        self.__spi.close()
        GPIO.cleanup()

    def show(self, image: Image):
        self.__display.display(image)
