from multiprocessing import Process, Queue

import RPi.GPIO as GPIO
from PIL import Image
from spidev import SpiDev

from core.decorator import override
from driver.ILI9486 import ILI9486, Origin
from interaction.Display import Display


class ILI9486Display(Display):

    __queue: Queue[tuple[Image.Image, int, int]] = Queue()
    __render_process: Process | None = None

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

    def __process_queue(self):
        while True:
            # if the queue is empty, the process will sleep
            image, x0, y0 = self.__queue.get()
            self.__display.display(image, x0, y0)

    @override
    def close(self):
        self.__display.reset()
        self.__spi.close()
        GPIO.cleanup()

    @override
    def show(self, image: Image.Image, x0: int, y0: int):
        self.__queue.put((image, x0, y0))
        if self.__render_process is None or not self.__render_process.is_alive():
            self.__render_process = Process(target=self.__process_queue, daemon=True)
            self.__render_process.start()

    def reset(self):
        self.__display.begin()
