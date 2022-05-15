from app.BaseApp import BaseApp
from PIL import ImageDraw


class NullApp(BaseApp):
    """Empty app to be used for testing purposes."""

    def __init__(self, title: str = 'NULL'):
        self.__title = title

    @property
    def title(self) -> str:
        return self.__title

    def draw(self, draw: ImageDraw) -> ImageDraw:
        pass

    def on_key_left(self):
        pass

    def on_key_up(self):
        pass

    def on_key_right(self):
        pass

    def on_key_down(self):
        pass

    def on_key_a(self):
        pass

    def on_key_b(self):
        pass
