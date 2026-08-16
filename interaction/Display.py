from abc import ABC, abstractmethod

from PIL import Image

from core.closeable import Closeable


class Display(Closeable, ABC):

    @abstractmethod
    def show(self, image: Image.Image, x0: int, y0: int):
        raise NotImplementedError
