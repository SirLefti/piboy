import time

from interface.BaseInterface import BaseInterface
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, constants
import threading


class TkInterface(BaseInterface):

    def __init__(self, width=480, height=320):
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


def _tk_thread(tk_interface: TkInterface):
    root = Tk()
    root.title('PiBoy Simulator - Tkinter')
    w, h = tk_interface.resolution
    canvas = Canvas(root, width=w, height=h)
    canvas.pack()
    while True:
        image = tk_interface.take_image()
        if image is not None:
            image_tk = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor=constants.NW, image=image_tk)
            root.update()
        root.update()
        time.sleep(.1)
