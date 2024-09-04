from core.decorator import override
from interaction.Display import Display
from PIL import Image
from driver.ILI9486 import ILI9486, Origin
from spidev import SpiDev
import RPi.GPIO as GPIO


class ILI9486Display(Display):

    def __init__(self, spi_config: tuple[int, int], dc_pin: int, rst_pin: int, flip_display: bool = False):
        GPIO.setmode(GPIO.BCM)
        bus, device = spi_config
        spi = SpiDev(bus, device)
        spi.mode = 0b10  # [CPOL|CPHA] -> polarity 1, phase 0
        spi.max_speed_hz = 64000000
        origin = Origin.LOWER_RIGHT if flip_display else Origin.UPPER_LEFT
        lcd = ILI9486(dc=dc_pin, rst=rst_pin, spi=spi, origin=origin).begin()
        self.__spi = spi
        self.__display = lcd
        self.__blocked = False  # Flag to block new draw calls while still drawing (takes around 333 ms)

    @override
    def close(self):
        self.__display.reset()
        self.__spi.close()
        GPIO.cleanup()

    @override
    def show(self, image: Image.Image, x0, y0):
        if not self.__blocked:
            self.__blocked = True
            self.__display.display(image, x0, y0)
            self.__blocked = False

    def reset(self):
        self.__display.begin()
