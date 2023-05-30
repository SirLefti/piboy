from app.App import App
from app.FileManagerApp import FileManagerApp
from app.UpdateApp import UpdateApp
from app.MapApp import MapApp
from app.NullApp import NullApp
from app.DebugApp import DebugApp
from app.ClockApp import ClockApp
from interface.Interface import Interface
from interface.Input import Input
from data.IPLocationProvider import IPLocationProvider
from data.OSMTileProvider import OSMTileProvider
from typing import List
from PIL import Image, ImageDraw
from datetime import datetime
from environment import Environment
import environment
import time


class AppState:

    def __init__(self, e: Environment):
        self.__environment = e
        self.__image_buffer = self.__init_buffer()
        self.__apps = []
        self.__active_app = 0

    def __init_buffer(self) -> Image:
        return Image.new('RGB', self.__environment.app_config.resolution, self.__environment.app_config.background)

    def clear_buffer(self) -> Image:
        self.__image_buffer = self.__init_buffer()
        return self.__image_buffer

    def add_app(self, app: App):
        self.__apps.append(app)
        return self

    @property
    def environment(self) -> Environment:
        return self.__environment

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

    def watch_function(self, interface: Interface):
        while True:
            now = datetime.now()
            # wait for next second
            time.sleep(1.0 - now.microsecond / 1000000.0)

            # draw the complete footer to remove existing clock display
            image, x0, y0 = draw_footer(self.image_buffer, self)
            interface.show(image, x0, y0)

    def update_display(self, interface: Interface, partial=False):
        """Draw call that handles the complete cycle of drawing a new image to the display."""
        image = self.clear_buffer()
        image = draw_base(image, self)
        image, x0, y0 = self.active_app.draw(image, partial)
        interface.show(image, x0, y0)

    def on_key_left(self, interface: Interface):
        self.active_app.on_key_left()
        self.update_display(interface, partial=True)

    def on_key_right(self, interface: Interface):
        self.active_app.on_key_right()
        self.update_display(interface, partial=True)

    def on_key_up(self, interface: Interface):
        self.active_app.on_key_up()
        self.update_display(interface, partial=True)

    def on_key_down(self, interface: Interface):
        self.active_app.on_key_down()
        self.update_display(interface, partial=True)

    def on_key_a(self, interface: Interface):
        self.active_app.on_key_a()
        self.update_display(interface, partial=True)

    def on_key_b(self, interface: Interface):
        self.active_app.on_key_b()
        self.update_display(interface, partial=True)

    def on_rotary_increase(self, interface: Interface):
        self.active_app.on_app_leave()
        self.next_app()
        self.active_app.on_app_enter()
        self.update_display(interface, partial=False)

    def on_rotary_decrease(self, interface: Interface):
        self.active_app.on_app_leave()
        self.previous_app()
        self.active_app.on_app_enter()
        self.update_display(interface, partial=False)


def draw_footer(image: Image, state: AppState) -> (Image, int, int):
    width, height = state.environment.app_config.resolution
    footer_height = 20  # height of the footer
    footer_bottom_offset = 3  # spacing to the bottom
    footer_side_offset = state.environment.app_config.app_side_offset  # spacing to the sides
    font = state.environment.app_config.font_header
    draw = ImageDraw.Draw(image)

    date_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    start = (footer_side_offset, height - footer_height - footer_bottom_offset)
    end = (width - footer_side_offset, height - footer_bottom_offset)
    draw.rectangle(start + end, fill=state.environment.app_config.accent_dark)
    _, _, text_width, text_height = font.getbbox(date_str)
    text_padding = (footer_height - text_height) / 2
    draw.text(
        (width - footer_side_offset - text_padding - text_width, height - footer_height - footer_bottom_offset +
         text_padding), date_str, state.environment.app_config.accent_dark, font=font)
    x0, y0 = start
    return image.crop(start + end), x0, y0


def draw_header(image: Image, state: AppState) -> (Image, int, int):
    width, height = state.environment.app_config.resolution
    vertical_line = 5  # vertical limiter line
    header_top_offset = state.environment.app_config.app_top_offset - vertical_line  # base for header
    header_side_offset = state.environment.app_config.app_side_offset  # spacing to the sides
    app_spacing = 20  # space between app headers
    app_padding = 5  # space around app header
    draw = ImageDraw.Draw(image)
    background = state.environment.app_config.background
    accent = state.environment.app_config.accent

    # draw base header lines
    start = (header_side_offset, header_top_offset + vertical_line)
    end = (header_side_offset, header_top_offset)
    draw.line(start + end, fill=accent)
    start = end
    end = (width - header_side_offset, header_top_offset)
    draw.line(start + end, fill=accent)
    start = end
    end = (width - header_side_offset, header_top_offset + vertical_line)
    draw.line(start + end, fill=accent)

    # draw app short name header
    font = state.environment.app_config.font_header
    max_text_width = width - (2 * header_side_offset)
    app_text_width = sum(font.getbbox(app.title)[2] for app in state.apps) + (len(state.apps) - 1) * app_spacing
    cursor = header_side_offset + (max_text_width - app_text_width) / 2
    for app in state.apps:
        _, _, text_width, text_height = font.getbbox(app.title)
        draw.text((cursor, header_top_offset - text_height - app_padding), app.title, accent, font=font)
        if app is state.active_app:
            start = (cursor - app_padding, header_top_offset - vertical_line)
            end = (cursor - app_padding, header_top_offset)
            draw.line(start + end, fill=accent)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset)
            draw.line(start + end, fill=background)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset - vertical_line)
            draw.line(start + end, fill=accent)
        cursor = cursor + text_width + app_spacing

    partial_start = (header_side_offset, 0)
    partial_end = (width - header_side_offset, header_top_offset + vertical_line)
    x0, y0 = partial_start
    return image.crop(partial_start + partial_end), x0, y0


def draw_base(image: Image, state: AppState) -> Image:
    draw_header(image, state)
    draw_footer(image, state)
    return image


def load_environment() -> Environment:
    environment.configure()
    try:
        return environment.load()
    except FileNotFoundError:
        e = Environment()
        environment.save(e)
        return e


if __name__ == '__main__':
    INTERFACE: Interface
    INPUT: Input

    env = load_environment()
    app_state = AppState(env)

    # wrapping key functions with local interface instance
    def on_key_left():
        app_state.on_key_left(INTERFACE)

    def on_key_right():
        app_state.on_key_right(INTERFACE)

    def on_key_up():
        app_state.on_key_up(INTERFACE)

    def on_key_down():
        app_state.on_key_down(INTERFACE)

    def on_key_a():
        app_state.on_key_a(INTERFACE)

    def on_key_b():
        app_state.on_key_b(INTERFACE)

    def on_rotary_increase():
        app_state.on_rotary_increase(INTERFACE)

    def on_rotary_decrease():
        app_state.on_rotary_decrease(INTERFACE)

    def update_display(partial=False):
        app_state.update_display(INTERFACE, partial)

    app_state.add_app(FileManagerApp()) \
        .add_app(UpdateApp()) \
        .add_app(NullApp('STAT')) \
        .add_app(NullApp('RAD')) \
        .add_app(DebugApp()) \
        .add_app(ClockApp(update_display, env.app_config.resolution, env.app_config.accent)) \
        .add_app(MapApp(update_display,
                        IPLocationProvider(apply_inaccuracy=True),
                        OSMTileProvider(env.app_config.background, env.app_config.accent, env.app_config.font_standard)
                        )
                 )

    if env.dev_mode:
        from interface.TkInterface import TkInterface

        __tk = TkInterface(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                           on_rotary_increase, on_rotary_decrease,
                           env.app_config.resolution, env.app_config.background, env.app_config.accent_dark)
        INTERFACE = __tk
        INPUT = __tk
    else:
        from interface.ILI9486Interface import ILI9486Interface
        from interface.GPIOInput import GPIOInput

        INTERFACE = ILI9486Interface(env.display_config, env.pin_config.dc_pin, env.pin_config.rst_pin, env.flip_display)
        INPUT = GPIOInput(env.pin_config.left_pin, env.pin_config.up_pin,
                          env.pin_config.right_pin, env.pin_config.down_pin,
                          env.pin_config.a_pin, env.pin_config.b_pin,
                          env.pin_config.clk_pin, env.pin_config.dt_pin, env.pin_config.sw_pin,
                          on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                          on_rotary_increase, on_rotary_decrease)

    # initial draw
    app_state.update_display(INTERFACE)
    app_state.active_app.on_app_enter()

    try:
        # blocking function that updates the clock
        app_state.watch_function(INTERFACE)
    except KeyboardInterrupt:
        pass
    finally:
        INTERFACE.close()
        INPUT.close()
