from interface.Interface import Interface
from interface.Input import Input
from typing import Callable
from PIL import Image, ImageTk
import tkinter as tk


class SelfManagedTkInterface(Interface, Input):

    BUTTON_W = 15
    BUTTON_H = 6

    def __init__(self, on_key_left: Callable, on_key_right: Callable,
                 on_key_up: Callable, on_key_down: Callable, on_key_a: Callable, on_key_b: Callable,
                 on_rotary_increase: Callable, on_rotary_decrease: Callable, on_rotary_switch: Callable,
                 resolution: tuple[int, int], background: tuple[int, int, int], ui_background: tuple[int, int, int]):
        Input.__init__(self, on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                       on_rotary_increase, on_rotary_decrease, on_rotary_switch)
        self.__on_key_left = on_key_left
        self.__on_key_right = on_key_right
        self.__on_key_up = on_key_up
        self.__on_key_down = on_key_down
        self.__on_key_a = on_key_a
        self.__on_key_b = on_key_b
        self.__on_rotary_increase = on_rotary_increase
        self.__on_rotary_decrease = on_rotary_decrease
        self.__resolution = resolution
        self.__background = background
        self.__image = Image.new('RGB', resolution, background)

        self.__root = tk.Tk()
        self.__root.title('PiBoy - Simulator')
        self.__root.configure(bg='#%02x%02x%02x' % ui_background)
        self.__image_tk = ImageTk.PhotoImage(self.__image)
        self.__label = tk.Label(self.__root, image=self.__image_tk)
        self.__label.grid(row=0, column=0, rowspan=4)

        button_left = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='left',
                                command=self.__on_key_left)
        button_left.grid(row=1, column=1)
        button_up = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='up',
                              command=self.__on_key_up)
        button_up.grid(row=0, column=2)
        button_right = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='right',
                                 command=self.__on_key_right)
        button_right.grid(row=1, column=3)
        button_down = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='down',
                                command=self.__on_key_down)
        button_down.grid(row=2, column=2)
        button_a = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='button a',
                             command=self.__on_key_a)
        button_a.grid(row=2, column=4)
        button_b = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='button b',
                             command=self.__on_key_b)
        button_b.grid(row=2, column=5)
        button_decrease = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='-',
                                    command=self.__on_rotary_decrease)
        button_decrease.grid(row=0, column=4)
        button_increase = tk.Button(self.__root, width=self.BUTTON_W, height=self.BUTTON_H, text='+',
                                    command=self.__on_rotary_increase)
        button_increase.grid(row=0, column=5)

    def show(self, image: Image.Image, x0, y0):
        self.__image.paste(image, (x0, y0))
        self.__image_tk = ImageTk.PhotoImage(self.__image)
        self.__label.configure(image=self.__image_tk)

    def close(self):
        pass

    def run(self):
        """blocking function to actually run the UI"""
        self.__root.mainloop()
