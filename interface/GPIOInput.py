from interface.Input import Input
from typing import Callable
import RPi.GPIO as GPIO
import evdev
import threading


class GPIOInput(Input):

    def __init__(self, key_left: int, key_up: int, key_right: int, key_down: int, key_a: int, key_b: int,
                 rotary_device: str, rotary_switch: int,
                 on_key_left: Callable, on_key_right: Callable, on_key_up: Callable, on_key_down: Callable,
                 on_key_a: Callable, on_key_b: Callable, on_rotary_increase: Callable, on_rotary_decrease: Callable,
                 on_rotary_switch: Callable, debounce: int = 50):
        super().__init__(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b, on_rotary_increase,
                         on_rotary_decrease, on_rotary_switch)
        self.__encoder = evdev.InputDevice(rotary_device)
        GPIO.setmode(GPIO.BCM)

        # keys setup
        GPIO.setup(key_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # rotary setup
        GPIO.setup(rotary_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # keys event callbacks
        GPIO.add_event_detect(key_left, GPIO.RISING, callback=self.__gpio_left, bouncetime=debounce)
        GPIO.add_event_detect(key_right, GPIO.RISING, callback=self.__gpio_right, bouncetime=debounce)
        GPIO.add_event_detect(key_up, GPIO.RISING, callback=self.__gpio_up, bouncetime=debounce)
        GPIO.add_event_detect(key_down, GPIO.RISING, callback=self.__gpio_down, bouncetime=debounce)
        GPIO.add_event_detect(key_a, GPIO.RISING, callback=self.__gpio_a, bouncetime=debounce)
        GPIO.add_event_detect(key_b, GPIO.RISING, callback=self.__gpio_b, bouncetime=debounce)

        # rotary event callbacks
        GPIO.add_event_detect(rotary_switch, GPIO.RISING, callback=self.__gpio_rotary_switch, bouncetime=debounce)

        loop_thread = threading.Thread(target=self.__encoder_loop)
        loop_thread.start()

    def __encoder_loop(self):
        # ref: https://github.com/raphaelyancey/pyKY040 (cannot use this lib directly, because it uses the old GPIO lib)
        for event in self.__encoder.read_loop():
            if event.type == 2:
                if event.value == -1:
                    self.on_rotary_increase()
                elif event.value == 1:
                    self.on_rotary_decrease()

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

    def __gpio_rotary_increase(self, pin):
        self.on_rotary_increase()

    def __gpio_rotary_decrease(self, pin):
        self.on_rotary_decrease()

    def __gpio_rotary_switch(self, pin):
        self.on_rotary_switch()
