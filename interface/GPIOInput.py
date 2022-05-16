from interface.BaseInput import BaseInput
from typing import Callable
import RPi.GPIO as GPIO


class GPIOInput(BaseInput):

    def __init__(self, key_left: int, key_up: int, key_right: int, key_down: int, key_a: int, key_b: int,
                 on_key_left: Callable, on_key_right: Callable, on_key_up: Callable, on_key_down: Callable,
                 on_key_a: Callable, on_key_b: Callable, on_rotary_increase: Callable, on_rotary_decrease: Callable,
                 bouncetime: int = 50):
        super().__init__(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b, on_rotary_increase,
                         on_rotary_decrease)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(key_left, GPIO.IN)
        GPIO.setup(key_right, GPIO.IN)
        GPIO.setup(key_up, GPIO.IN)
        GPIO.setup(key_down, GPIO.IN)
        GPIO.setup(key_a, GPIO.IN)
        GPIO.setup(key_b, GPIO.IN)
        GPIO.add_event_detect(key_left, GPIO.RISING, callback=on_key_left, bouncetime=bouncetime)
        GPIO.add_event_detect(key_up, GPIO.RISING, callback=on_key_up, bouncetime=bouncetime)
        GPIO.add_event_detect(key_right, GPIO.RISING, callback=on_key_right, bouncetime=bouncetime)
        GPIO.add_event_detect(key_down, GPIO.RISING, callback=on_key_down, bouncetime=bouncetime)
        GPIO.add_event_detect(key_a, GPIO.RISING, callback=on_key_a, bouncetime=bouncetime)
        GPIO.add_event_detect(key_b, GPIO.RISING, callback=on_key_b, bouncetime=bouncetime)
