from PIL import Image

from app.App import App
from core.decorator import override


class NullApp(App):
    """Empty app to be used for testing purposes."""

    def __init__(self, title: str = 'NULL'):
        self.__title = title

    @property
    @override
    def title(self) -> str:
        return self.__title

    @override
    def draw(self, image: Image.Image, partial=False) -> tuple[Image, int, int]:
        return image, 0, 0
