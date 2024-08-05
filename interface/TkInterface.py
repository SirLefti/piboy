from interface.Interface import Interface
from interface.Input import Input
from typing import Callable, Optional
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button, constants, TclError
import threading
import time


class TkInterface(Interface, Input):

    def __init__(self, on_key_left: Callable, on_key_right: Callable,
                 on_key_up: Callable, on_key_down: Callable, on_key_a: Callable, on_key_b: Callable,
                 on_rotary_increase: Callable, on_rotary_decrease: Callable, on_rotary_switch: Callable,
                 resolution: tuple[int, int], background: tuple[int, int, int], ui_background: tuple[int, int, int]):
        Input.__init__(self, on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                       on_rotary_increase, on_rotary_decrease, on_rotary_switch)
        self.__resolution = resolution
        self.__background = background
        self.__image: Optional[Image.Image] = None
        self.__buffer: Optional[Image.Image] = None
        threading.Thread(target=_tk_thread, args=(self, resolution, ui_background), daemon=True).start()

    def close(self):
        pass

    def take_image(self) -> Optional[Image.Image]:
        image = self.__image
        self.__image = None
        return image

    def show(self, image: Image.Image, x0, y0):
        if self.__buffer is None:
            self.__buffer = Image.new('RGB', self.__resolution, self.__background)
        self.__buffer.paste(image, (x0, y0))  # overwrites __buffer
        self.__image = self.__buffer  # thus assigning __buffer to __image


BUTTON_W = 15
BUTTON_H = 6


def _tk_thread(tk_interface: TkInterface, resolution: tuple[int, int], ui_background: tuple[int, int, int]):
    root = Tk()
    root.title('PiBoy Simulator - Tkinter')
    bg_color_hex = '#%02x%02x%02x' % ui_background
    root.configure(bg=bg_color_hex)
    w, h = resolution
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
