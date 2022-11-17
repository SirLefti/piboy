from interface.BaseInput import BaseInput
from typing import Callable
import RPi.GPIO as GPIO


class GPIOInput(BaseInput):

    def __init__(self, key_left: int, key_up: int, key_right: int, key_down: int, key_a: int, key_b: int,
                 rotary_clock: int, rotary_data: int, rotary_switch: int,
                 on_key_left: Callable, on_key_right: Callable, on_key_up: Callable, on_key_down: Callable,
                 on_key_a: Callable, on_key_b: Callable, on_rotary_increase: Callable, on_rotary_decrease: Callable,
                 debounce: int = 50):
        super().__init__(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b, on_rotary_increase,
                         on_rotary_decrease)
        self.__rotary_clock = rotary_clock
        self.__rotary_data = rotary_data
        GPIO.setmode(GPIO.BCM)

        # keys setup
        GPIO.setup(key_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # rotary setup
        GPIO.setup(rotary_clock, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(rotary_data, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(rotary_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # keys event callbacks
        GPIO.add_event_detect(key_left, GPIO.RISING, callback=self.__gpio_left, bouncetime=debounce)
        GPIO.add_event_detect(key_right, GPIO.RISING, callback=self.__gpio_right, bouncetime=debounce)
        GPIO.add_event_detect(key_up, GPIO.RISING, callback=self.__gpio_up, bouncetime=debounce)
        GPIO.add_event_detect(key_down, GPIO.RISING, callback=self.__gpio_down, bouncetime=debounce)
        GPIO.add_event_detect(key_a, GPIO.RISING, callback=self.__gpio_a, bouncetime=debounce)
        GPIO.add_event_detect(key_b, GPIO.RISING, callback=self.__gpio_b, bouncetime=debounce)

        # rotary event callbacks
        GPIO.add_event_detect(rotary_clock, GPIO.RISING, callback=self.__gpio_rotary_clock, bouncetime=debounce)
        GPIO.add_event_detect(rotary_switch, GPIO.RISING, callback=self.__gpio_rotary_switch, bouncetime=debounce)

    def close(self):
        GPIO.cleanup()

    def __gpio_left(self, pin):
        self.on_key_left()

    def __gpio_right(self, pin):
        self.on_key_right()

    def __gpio_up(self, pin):
        self.on_key_up()

    def __gpio_down(self, pin):
        self.on_key_down()

    def __gpio_a(self, pin):
        self.on_key_a()

    def __gpio_b(self, pin):
        self.on_key_b()

    def __gpio_rotary_clock(self, pin):
        clk = GPIO.input(self.__rotary_clock)
        dt = GPIO.input(self.__rotary_data)
        if clk == 0 and dt == 0:
            self.on_rotary_decrease()
        elif clk == 0 and dt == 1:
            self.on_rotary_increase()

    def __gpio_rotary_switch(self, pin):
        pass
