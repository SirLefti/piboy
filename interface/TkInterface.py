import config
from interface.BaseInterface import BaseInterface
from interface.BaseInput import BaseInput
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button, constants, TclError, Event
import threading
import time


class TkInterface(BaseInterface, BaseInput):

    def __init__(self, width=480, height=320):
        self.__on_key_left = config.ON_KEY_LEFT
        self.__on_key_up = config.ON_KEY_UP
        self.__on_key_right = config.ON_KEY_RIGHT
        self.__on_key_down = config.ON_KEY_DOWN
        self.__on_key_a = config.ON_KEY_A
        self.__on_key_b = config.ON_KEY_B
        self.__on_rotary_increase = config.ON_ROTARY_INCREASE
        self.__on_rotary_decrease = config.ON_ROTARY_DECREASE
        self.__width = width
        self.__height = height
        self.__image = None
        threading.Thread(target=_tk_thread, args=(self,), daemon=True).start()

    @property
    def resolution(self) -> tuple:
        return self.__width, self.__height

    def take_image(self) -> Image:
        image = self.__image
        self.__image = None
        return image

    def show(self, image: Image):
        self.__image = image

    def on_key_left(self):
        self.__on_key_left()

    def on_key_up(self):
        self.__on_key_up()

    def on_key_right(self):
        self.__on_key_right()

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


BUTTON_W = 15
BUTTON_H = 6


def _tk_thread(tk_interface: TkInterface):
    root = Tk()
    root.title('PiBoy Simulator - Tkinter')
    bg_color_hex = '#%02x%02x%02x' % config.ACCENT_DARK
    root.configure(bg=bg_color_hex)
    w, h = tk_interface.resolution
    canvas = Canvas(root, width=w, height=h)
    canvas.grid(row=1, column=1, rowspan=4)

    # buttons
    button_left = Button(root, text='left', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_key_left)
    button_left.grid(row=2, column=2)
    button_up = Button(root, text='up', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_key_up)
    button_up.grid(row=1, column=3)
    button_right = Button(root, text='right', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_key_right)
    button_right.grid(row=2, column=4)
    button_down = Button(root, text='down', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_key_down)
    button_down.grid(row=3, column=3)
    button_a = Button(root, text='button a', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_key_a)
    button_a.grid(row=3, column=5)
    button_b = Button(root, text='button b', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_key_b)
    button_b.grid(row=3, column=6)
    button_decrease = Button(root, text='-', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_rotary_decrease)
    button_decrease.grid(row=1, column=5)
    button_increase = Button(root, text='+', width=BUTTON_W, height=BUTTON_H, command=tk_interface.on_rotary_increase)
    button_increase.grid(row=1, column=6)

    alive = True
    while alive:
        try:
            image = tk_interface.take_image()
            if image is not None:
                # doing this to avoid the image being garbage-collected
                image_tk = ImageTk.PhotoImage(image)
                canvas.create_image(0, 0, anchor=constants.NW, image=image_tk)
                root.update()
            root.update()
            time.sleep(.1)
        except TclError:
            # stop the loop if root has been destroyed
            alive = False
