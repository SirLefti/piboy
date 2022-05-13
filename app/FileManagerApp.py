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
        text_width, text_height = font.getsize(home)
        draw.text((config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET), home, config.ACCENT, font=font)
        return draw
