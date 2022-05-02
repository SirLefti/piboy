from interface.BaseInterface import BaseInterface
from PIL import Image


class PillowInterface(BaseInterface):

    def __init__(self, width=480, height=320):
        self.__width = width
        self.__height = height

    @property
    def resolution(self) -> tuple:
        return self.__width, self.__height

    def show(self, image: Image):
        image.show()
