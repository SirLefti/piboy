from abc import ABC, abstractmethod
from PIL import Image


class Interface(ABC):

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def show(self, image: Image, x0, y0):
        raise NotImplementedError
