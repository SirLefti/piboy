from app.BaseApp import BaseApp
from PIL import Image


class FileManagerApp(BaseApp):

    def __init__(self):
        pass

    @property
    def title(self) -> str:
        return "INV"

    def draw(self, image: Image) -> Image:
        pass
