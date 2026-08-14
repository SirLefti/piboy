import logging
import threading
from collections import deque

from PIL import Image
from pyili9486 import ILI9486, Origin
from pyili9486.gpio.rpilgpio_facade import RPiLGPIOFacade
from spidev import SpiDev

from core.decorator import override
from interaction.Display import Display

Patch = tuple[Image.Image, int, int]
Bounds = tuple[int, int, int, int]

logger = logging.getLogger('display')

class ILI9486Display(Display):

    __queue: deque[Patch] = deque()
    __render_thread: threading.Thread | None = None
    __condition = threading.Condition()

    def __init__(self, spi_config: tuple[int, int], dc_pin: int, rst_pin: int, flip_display: bool = False):
        bus, device = spi_config
        spi = SpiDev(bus, device)
        spi.mode = 0b10  # [CPOL|CPHA] -> polarity 1, phase 0
        spi.max_speed_hz = 64000000
        origin = Origin.LOWER_RIGHT if flip_display else Origin.UPPER_LEFT
        gpio = RPiLGPIOFacade(dc_pin, rst_pin)
        lcd = ILI9486(spi=spi, gpio_facade=gpio, origin=origin).begin()
        self.__spi = spi
        self.__display = lcd

        t = threading.Thread(target=self.__process_queue, args=(), daemon=True)
        t.start()
        self.__render_thread = t

    @staticmethod
    def __bounds(patch: Patch) -> Bounds:
        image, x0, y0 = patch
        width, height = image.size
        return x0, y0, x0 + width, y0 + height

    @staticmethod
    def __contains(outer: Bounds, inner: Bounds) -> bool:
        outer_x0, outer_y0, outer_x1, outer_y1 = outer
        inner_x0, inner_y0, inner_x1, inner_y1 = inner
        return outer_x0 <= inner_x0 and outer_y0 <= inner_y0 and outer_x1 >= inner_x1 and outer_y1 >= inner_y1

    def __process_queue(self):
        while True:
            with self.__condition:
                while not self.__queue:
                    self.__condition.wait()
                image, x0, y0 = self.__queue.popleft()
            self.__display.display(image, x0, y0)

    @override
    def close(self):
        self.__display.reset()
        self.__spi.close()

    @override
    def show(self, image: Image.Image, x0: int, y0: int):
        new_patch = (image, x0, y0)
        new_bounds = self.__bounds(new_patch)
        with self.__condition:
            # drop any not-yet-drawn patches the new one fully covers, because they would be overwritten anyway
            optimized_deque = deque(p for p in self.__queue if not self.__contains(new_bounds, self.__bounds(p)))
            if len(optimized_deque) != len(self.__queue):
                logger.debug(f"dropped {len(self.__queue) - len(optimized_deque)} patches")
            self.__queue = optimized_deque
            self.__queue.append((image, x0, y0))
            self.__condition.notify()

    def reset(self):
        self.__display.begin()
