from app.BaseApp import BaseApp
from PIL import ImageDraw


class NullApp(BaseApp):
    """Empty app to be used for testing purposes."""

    def __init__(self, title: str = 'NULL'):
        self.__title = title

    @property
    def title(self) -> str:
        return self.__title

    def draw(self, image: ImageDraw) -> ImageDraw:
        pass
