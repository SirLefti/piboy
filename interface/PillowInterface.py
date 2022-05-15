from typing import Tuple

from interface.BaseInterface import BaseInterface
from PIL import Image


class PillowInterface(BaseInterface):

    def __init__(self, width: int = 480, height: int = 320):
        self.__width = width
        self.__height = height

    @property
    def resolution(self) -> Tuple[int, int]:
        return self.__width, self.__height

    def show(self, image: Image):
        image.show()
