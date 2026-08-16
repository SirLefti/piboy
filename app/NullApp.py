from typing import Any, Generator

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
    def draw(self, image: Image.Image, partial=False) -> Generator[tuple[Image.Image, int, int], Any, None]:
        yield image, 0, 0
