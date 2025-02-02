from abc import ABC, abstractmethod

from PIL import Image


class Display(ABC):

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def show(self, image: Image.Image, x0: int, y0: int):
        raise NotImplementedError
