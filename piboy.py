from app.App import App
from app.FileManagerApp import FileManagerApp
from app.MapApp import MapApp
from app.NullApp import NullApp
from interface.Interface import Interface
from interface.Input import Input
from data.IPLocationProvider import IPLocationProvider
from data.OSMTileProvider import OSMTileProvider
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

    def clear_buffer(self) -> Image:
        self.__image_buffer = self.__init_buffer()
        return self.__image_buffer

    def add_app(self, app: App):
        self.__apps.append(app)
        return self

    @property
    def image_buffer(self) -> Image:
        return self.__image_buffer

    @property
    def apps(self) -> List[App]:
        return self.__apps

    @property
    def active_app(self) -> App:
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
    update_display(partial=True)


def on_key_right():
    STATE.active_app.on_key_right()
    update_display(partial=True)


def on_key_up():
    STATE.active_app.on_key_up()
    update_display(partial=True)


def on_key_down():
    STATE.active_app.on_key_down()
    update_display(partial=True)


def on_key_a():
    STATE.active_app.on_key_a()
    update_display(partial=True)


def on_key_b():
    STATE.active_app.on_key_b()
    update_display(partial=True)


def on_rotary_increase():
    STATE.active_app.on_app_leave()
    STATE.next_app()
    update_display(partial=False)
    STATE.active_app.on_app_enter()


def on_rotary_decrease():
    STATE.active_app.on_app_leave()
    STATE.previous_app()
    update_display(partial=False)
    STATE.active_app.on_app_enter()


INTERFACE: Interface
INPUT: Input

if config.DEV_MODE:
    from interface.TkInterface import TkInterface

    __tk = TkInterface(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                       on_rotary_increase, on_rotary_decrease, config.RESOLUTION, config.BACKGROUND)
    INTERFACE = __tk
    INPUT = __tk
else:
    from interface.ILI9486Interface import ILI9486Interface
    from interface.GPIOInput import GPIOInput

    INTERFACE = ILI9486Interface(config.FLIP_DISPLAY)
    INPUT = GPIOInput(config.LEFT_PIN, config.UP_PIN, config.RIGHT_PIN, config.DOWN_PIN, config.A_PIN, config.B_PIN,
                      config.CLK_PIN, config.DT_PIN, config.SW_PIN,
                      on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                      on_rotary_increase, on_rotary_decrease)


def watch_function():
    while True:
        now = datetime.now()
        # wait for next second
        time.sleep(1.0 - now.microsecond / 1000000.0)

        # draw the complete footer to remove existing clock display
        image, x0, y0 = draw_footer(STATE.image_buffer)
        INTERFACE.show(image, x0, y0)



def update_display(partial = False):
    """Draw call than handles the complete cycle of drawing a new image to the display."""
    image = STATE.clear_buffer()
    image = draw_base(image)
    image, x0, y0 = STATE.active_app.draw(image, partial)
    print(f'drawing {image.size} at {x0, y0}')
    INTERFACE.show(image, x0, y0)


STATE.add_app(FileManagerApp()) \
    .add_app(NullApp('DATA')) \
    .add_app(NullApp('STATS')) \
    .add_app(NullApp('RADIO')) \
    .add_app(MapApp(update_display, IPLocationProvider(apply_inaccuracy=True), OSMTileProvider()))


def draw_footer(image: Image) -> (Image, int, int):
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
    _, _, text_width, text_height = font.getbbox(date_str)
    text_padding = (footer_height - text_height) / 2
    draw.text((width - footer_side_offset - text_padding - text_width, height - footer_height - footer_bottom_offset +
               text_padding), date_str, config.ACCENT, font=font)
    x0, y0 = start
    return image.crop(start + end), x0, y0


def draw_header(image: Image) -> (Image, int, int):
    width, height = config.RESOLUTION
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
    app_text_width = sum(font.getbbox(app.title)[2] for app in STATE.apps) + (len(STATE.apps) - 1) * app_spacing
    cursor = header_side_offset + (max_text_width - app_text_width) / 2
    for app in STATE.apps:
        _, _, text_width, text_height = font.getbbox(app.title)
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

    partial_start = (header_side_offset, 0)
    partial_end = (width - header_side_offset, header_top_offset + vertical_line)
    x0, y0 = partial_start
    return image.crop(partial_start + partial_end), x0, y0


def draw_base(image: Image) -> Image:
    draw_header(image)
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
