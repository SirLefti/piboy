from app.BaseApp import BaseApp
from PIL import ImageDraw, ImageFont
import config
import os


class FileManagerApp(BaseApp):

    def __init__(self):
        pass

    @property
    def title(self) -> str:
        return "INV"

    def draw(self, draw: ImageDraw) -> ImageDraw:
        home = os.path.expanduser('~')
        content = os.listdir(home)
        font = ImageFont.truetype(config.FONT, 14)
        t_w, t_h = font.getsize(home)
        draw.text((50, 31), home, config.ACCENT, font=font)
        return draw
