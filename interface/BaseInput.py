from abc import ABC
from typing import Callable


class BaseInput(ABC):

    def __init__(self, on_key_left: Callable, on_key_right: Callable, on_key_up: Callable, on_key_down: Callable,
                 on_key_a: Callable, on_key_b: Callable, on_rotary_increase: Callable, on_rotary_decrease: Callable):
        self.__on_key_left = on_key_left
        self.__on_key_right = on_key_right
        self.__on_key_up = on_key_up
        self.__on_key_down = on_key_down
        self.__on_key_a = on_key_a
        self.__on_key_b = on_key_b
        self.__on_rotary_increase = on_rotary_increase
        self.__on_rotary_decrease = on_rotary_decrease

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

    def on_rotary_increase(self):
        self.__on_rotary_increase()

    def on_rotary_decrease(self):
        self.__on_rotary_decrease()
