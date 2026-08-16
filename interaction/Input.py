from abc import ABC
from typing import Callable

from core.closeable import Closeable


class Input(Closeable, ABC):

    def __init__(self, on_key_left: Callable[[], None], on_key_right: Callable[[], None],
                 on_key_up: Callable[[], None], on_key_down: Callable[[], None],
                 on_key_a: Callable[[], None], on_key_b: Callable[[], None],
                 on_rotary_change: Callable[[int], None], on_rotary_switch: Callable[[], None]):
        self.__on_key_left = on_key_left
        self.__on_key_right = on_key_right
        self.__on_key_up = on_key_up
        self.__on_key_down = on_key_down
        self.__on_key_a = on_key_a
        self.__on_key_b = on_key_b
        self.__on_rotary_change = on_rotary_change
        self.__on_rotary_switch = on_rotary_switch

    def on_key_left(self):
        self.__on_key_left()

    def on_key_right(self):
        self.__on_key_right()

    def on_key_up(self):
        self.__on_key_up()

    def on_key_down(self):
        self.__on_key_down()

    def on_key_a(self):
        self.__on_key_a()

    def on_key_b(self):
        self.__on_key_b()

    def on_rotary_change(self, steps: int):
        self.__on_rotary_change(steps)

    def on_rotary_switch(self):
        self.__on_rotary_switch()
