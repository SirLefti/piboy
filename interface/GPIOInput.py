from BaseInput import BaseInput
import RPi.GPIO as GPIO


class GPIOInput(BaseInput):

    def __init__(self, key_left: int, key_up: int, key_right: int, key_down: int, key_a: int, key_b: int,
                 bouncetime: int = 50):
        GPIO.setmode(GPIO.BCM)
        GPIO.add_event_detect(key_left, GPIO.RISING, callback=self.on_key_left, bouncetime=bouncetime)
        GPIO.add_event_detect(key_up, GPIO.RISING, callback=self.on_key_up, bouncetime=bouncetime)
        GPIO.add_event_detect(key_right, GPIO.RISING, callback=self.on_key_right, bouncetime=bouncetime)
        GPIO.add_event_detect(key_down, GPIO.RISING, callback=self.on_key_down, bouncetime=bouncetime)
        GPIO.add_event_detect(key_a, GPIO.RISING, callback=self.on_key_a, bouncetime=bouncetime)
        GPIO.add_event_detect(key_b, GPIO.RISING, callback=self.on_key_b, bouncetime=bouncetime)

    def on_key_left(self):
        pass

    def on_key_up(self):
        pass

    def on_key_right(self):
        pass

    def on_key_down(self):
        pass

    def on_key_a(self):
        pass

    def on_key_b(self):
        pass

    def on_rotary_increase(self):
        pass

    def on_rotary_decrease(self):
        pass
