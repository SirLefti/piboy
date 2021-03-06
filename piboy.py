from app.BaseApp import BaseApp
from app.FileManagerApp import FileManagerApp
from app.MapApp import MapApp
from app.NullApp import NullApp
from interface.BaseInterface import BaseInterface
from interface.BaseInput import BaseInput
from interface.TkInterface import TkInterface
from util.IPLocationProvider import IPLocationProvider
from util.OSMTileProvider import OSMTileProvider
import config
from typing import List, Tuple
from PIL import Image, ImageDraw
import time
from datetime import datetime


class AppState:

    def __init__(self, resolution: Tuple[int, int], background: Tuple[int, int, int]):
        self.__resolution = resolution
        self.__background = background
        self.__image_buffer = self.__init_buffer()
        self.__apps = []
        self.__active_app = 0

    def __init_buffer(self) -> Image:
        return Image.new('RGB', self.__resolution, self.__background)

    def clear_buffer(self):
        self.__image_buffer = self.__init_buffer()

    def add_app(self, app: BaseApp):
        self.__apps.append(app)
        return self

    @property
    def image_buffer(self) -> Image:
        return self.__image_buffer

    @property
    def apps(self) -> List[BaseApp]:
        return self.__apps

    @property
    def active_app(self) -> BaseApp:
        return self.__apps[self.__active_app]

    @property
    def active_app_index(self) -> int:
        return self.__active_app

    def next_app(self):
        self.__active_app += 1
        if not self.__active_app < len(self.__apps):
            self.__active_app = 0

    def previous_app(self):
        self.__active_app -= 1
        if self.__active_app < 0:
            self.__active_app = len(self.__apps) - 1


STATE = AppState(config.RESOLUTION, config.BACKGROUND)


def on_key_left():
    STATE.active_app.on_key_left()
    update_display()


def on_key_right():
    STATE.active_app.on_key_right()
    update_display()


def on_key_up():
    STATE.active_app.on_key_up()
    update_display()


def on_key_down():
    STATE.active_app.on_key_down()
    update_display()


def on_key_a():
    STATE.active_app.on_key_a()
    update_display()


def on_key_b():
    STATE.active_app.on_key_b()
    update_display()


def on_rotary_increase():
    STATE.active_app.on_app_leave()
    STATE.next_app()
    update_display()
    STATE.active_app.on_app_enter()


def on_rotary_decrease():
    STATE.active_app.on_app_leave()
    STATE.previous_app()
    update_display()
    STATE.active_app.on_app_enter()


__tk = TkInterface(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                   on_rotary_increase, on_rotary_decrease)
INTERFACE: BaseInterface = __tk
INPUT: BaseInput = __tk


def watch_function():
    while True:
        now = datetime.now()
        # wait for next second
        time.sleep(1.0 - now.microsecond / 1000000.0)

        # draw the complete footer to remove existing clock display
        draw_footer(STATE.image_buffer)
        INTERFACE.show(STATE.image_buffer)


def update_display():
    """Draw call than handles the complete cycle of drawing a new image to the display."""
    STATE.clear_buffer()
    image = STATE.image_buffer
    # image = Image.new('RGB', config.RESOLUTION, config.BACKGROUND)
    draw_base(image, config.RESOLUTION)
    STATE.active_app.draw(image)
    INTERFACE.show(image)


STATE.add_app(FileManagerApp()).add_app(NullApp('DATA')).add_app(NullApp('STATS')).add_app(NullApp('RADIO')).add_app(
    MapApp(INTERFACE, update_display, IPLocationProvider(apply_inaccuracy=True), OSMTileProvider())
)


def draw_footer(image: Image) -> Image:
    width, height = config.RESOLUTION
    footer_height = 20  # height of the footer
    footer_bottom_offset = 3  # spacing to the bottom
    footer_side_offset = config.APP_SIDE_OFFSET  # spacing to the sides
    font = config.FONT_HEADER
    draw = ImageDraw.Draw(image)

    date_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    start = (footer_side_offset, height - footer_height - footer_bottom_offset)
    end = (width - footer_side_offset, height - footer_bottom_offset)
    draw.rectangle(start + end, fill=config.ACCENT_DARK)
    text_width, text_height = font.getsize(date_str)
    text_padding = (footer_height - text_height) / 2
    draw.text((width - footer_side_offset - text_padding - text_width, height - footer_height - footer_bottom_offset +
               text_padding), date_str, config.ACCENT, font=font)
    return image


def draw_base(image: Image, resolution: Tuple[int, int]) -> Image:
    width, height = resolution
    vertical_line = 5  # vertical limiter line
    header_top_offset = config.APP_TOP_OFFSET - vertical_line  # base for header
    header_side_offset = config.APP_SIDE_OFFSET  # spacing to the sides
    app_spacing = 20  # space between app headers
    app_padding = 5  # space around app header
    draw = ImageDraw.Draw(image)

    # draw base header lines
    start = (header_side_offset, header_top_offset + vertical_line)
    end = (header_side_offset, header_top_offset)
    draw.line(start + end, fill=config.ACCENT)
    start = end
    end = (width - header_side_offset, header_top_offset)
    draw.line(start + end, fill=config.ACCENT)
    start = end
    end = (width - header_side_offset, header_top_offset + vertical_line)
    draw.line(start + end, fill=config.ACCENT)

    # draw app short name header
    font = config.FONT_HEADER
    max_text_width = width - (2 * header_side_offset)
    app_text_width = sum(font.getsize(app.title)[0] for app in STATE.apps) + (len(STATE.apps) - 1) * app_spacing
    cursor = header_side_offset + (max_text_width - app_text_width) / 2
    for app in STATE.apps:
        text_width, text_height = font.getsize(app.title)
        draw.text((cursor, header_top_offset - text_height - app_padding), app.title, config.ACCENT, font=font)
        if app is STATE.active_app:
            start = (cursor - app_padding, header_top_offset - vertical_line)
            end = (cursor - app_padding, header_top_offset)
            draw.line(start + end, fill=config.ACCENT)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset)
            draw.line(start + end, fill=config.BACKGROUND)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset - vertical_line)
            draw.line(start + end, fill=config.ACCENT)
        cursor = cursor + text_width + app_spacing

    # draw footer
    draw_footer(image)
    return image


if __name__ == '__main__':
    # initial draw
    update_display()
    STATE.active_app.on_app_enter()

    try:
        # blocking function that updates the clock
        watch_function()
    except KeyboardInterrupt:
        pass
    finally:
        INTERFACE.close()
        INPUT.close()
