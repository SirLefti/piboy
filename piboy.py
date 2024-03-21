from app.App import App
from app.FileManagerApp import FileManagerApp
from app.RadioApp import RadioApp
from app.UpdateApp import UpdateApp
from app.MapApp import MapApp
from app.DebugApp import DebugApp
from app.ClockApp import ClockApp
from app.EnvironmentApp import EnvironmentApp
from data.LocationProvider import LocationProvider
from data.EnvironmentDataProvider import EnvironmentDataProvider
from interface.Interface import Interface
from interface.Input import Input
from data.OSMTileProvider import OSMTileProvider
from PIL import Image, ImageDraw
from datetime import datetime
from environment import Environment
import environment
import time


class AppState:

    def __init__(self, e: Environment):
        self.__environment = e
        self.__image_buffer = self.__init_buffer()
        self.__apps: list[App] = []
        self.__active_app = 0

    def __init_buffer(self) -> Image.Image:
        return Image.new('RGB', self.__environment.app_config.resolution, self.__environment.app_config.background)

    def clear_buffer(self) -> Image.Image:
        self.__image_buffer = self.__init_buffer()
        return self.__image_buffer

    def add_app(self, app: App) -> 'AppState':
        self.__apps.append(app)
        return self

    @property
    def environment(self) -> Environment:
        return self.__environment

    @property
    def image_buffer(self) -> Image.Image:
        return self.__image_buffer

    @property
    def apps(self) -> list[App]:
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


def draw_footer(image: Image.Image, state: AppState) -> tuple[Image.Image, int, int]:
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
         text_padding), date_str, state.environment.app_config.accent, font=font)
    x0, y0 = start
    return image.crop(start + end), x0, y0


def draw_header(image: Image.Image, state: AppState) -> tuple[Image.Image, int, int]:
    width, height = state.environment.app_config.resolution
    vertical_line = 5  # vertical limiter line
    header_top_offset = state.environment.app_config.app_top_offset - vertical_line  # base for header
    header_side_offset = state.environment.app_config.app_side_offset  # spacing to the sides
    app_spacing = 20  # space between app headers
    app_padding = 5  # space around app header
    draw = ImageDraw.Draw(image)
    color_background = state.environment.app_config.background
    color_accent = state.environment.app_config.accent

    # draw base header lines
    start = (header_side_offset, header_top_offset + vertical_line)
    end = (header_side_offset, header_top_offset)
    draw.line(start + end, fill=color_accent)
    start = end
    end = (width - header_side_offset, header_top_offset)
    draw.line(start + end, fill=color_accent)
    start = end
    end = (width - header_side_offset, header_top_offset + vertical_line)
    draw.line(start + end, fill=color_accent)

    # draw app short name header
    font = state.environment.app_config.font_header
    max_text_width = width - (2 * header_side_offset)
    app_text_width = sum(font.getbbox(app.title)[2] for app in state.apps) + (len(state.apps) - 1) * app_spacing
    cursor = header_side_offset + (max_text_width - app_text_width) // 2
    for app in state.apps:
        _, _, text_width, text_height = font.getbbox(app.title)
        draw.text((cursor, header_top_offset - text_height - app_padding), app.title, color_accent, font=font)
        if app is state.active_app:
            start = (cursor - app_padding, header_top_offset - vertical_line)
            end = (cursor - app_padding, header_top_offset)
            draw.line(start + end, fill=color_accent)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset)
            draw.line(start + end, fill=color_background)
            start = end
            end = (cursor + text_width + app_padding, header_top_offset - vertical_line)
            draw.line(start + end, fill=color_accent)
        cursor = cursor + text_width + app_spacing

    partial_start = (header_side_offset, 0)
    partial_end = (width - header_side_offset, header_top_offset + vertical_line)
    x0, y0 = partial_start
    return image.crop(partial_start + partial_end), x0, y0


def draw_base(image: Image.Image, state: AppState) -> Image.Image:
    draw_header(image, state)
    draw_footer(image, state)
    return image


def is_raspberry_pi() -> bool:
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as model_info:
            return 'Raspberry Pi' in model_info.read()
    except FileNotFoundError:
        return False


def load_environment() -> Environment:
    environment.configure()
    try:
        return environment.load()
    except FileNotFoundError:
        e = Environment()
        e.dev_mode = not is_raspberry_pi()
        environment.save(e)
        return e


if __name__ == '__main__':
    INTERFACE: Interface
    INPUT: Input

    env = load_environment()
    resolution = env.app_config.resolution
    background = env.app_config.background
    color = env.app_config.accent
    color_dark = env.app_config.accent_dark
    font_standard = env.app_config.font_standard
    top_offset = env.app_config.app_top_offset
    side_offset = env.app_config.app_side_offset
    bottom_offset = env.app_config.app_bottom_offset

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

    ENVIRONMENT_DATA_PROVIDER: EnvironmentDataProvider
    LOCATION_PROVIDER: LocationProvider

    if env.dev_mode:
        from interface.TkInterface import TkInterface
        from data.FakeEnvironmentDataProvider import FakeEnvironmentDataProvider
        from data.IPLocationProvider import IPLocationProvider

        __tk = TkInterface(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                           on_rotary_increase, on_rotary_decrease,
                           resolution, background, color_dark)
        INTERFACE = __tk
        INPUT = __tk
        ENVIRONMENT_DATA_PROVIDER = FakeEnvironmentDataProvider()
        LOCATION_PROVIDER = IPLocationProvider(apply_inaccuracy=True)
    else:
        from interface.ILI9486Interface import ILI9486Interface
        from interface.GPIOInput import GPIOInput
        from data.BME280EnvironmentDataProvider import BME280EnvironmentDataProvider
        from data.SerialGPSLocationProvider import SerialGPSLocationProvider

        display_spi = (env.display_config.bus, env.display_config.device)
        INTERFACE = ILI9486Interface(display_spi, env.pin_config.dc_pin, env.pin_config.rst_pin, env.flip_display)
        INPUT = GPIOInput(env.pin_config.left_pin, env.pin_config.up_pin,
                          env.pin_config.right_pin, env.pin_config.down_pin,
                          env.pin_config.a_pin, env.pin_config.b_pin,
                          env.pin_config.clk_pin, env.pin_config.dt_pin, env.pin_config.sw_pin,
                          on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                          on_rotary_increase, on_rotary_decrease)
        ENVIRONMENT_DATA_PROVIDER = BME280EnvironmentDataProvider(env.env_sensor_config.port,
                                                                  env.env_sensor_config.address)
        LOCATION_PROVIDER = SerialGPSLocationProvider(env.gps_module_config.port, env.gps_module_config.baudrate)

    app_state.add_app(FileManagerApp(resolution, background, color, color_dark, top_offset, side_offset, bottom_offset,
                                     font_standard)) \
        .add_app(UpdateApp(resolution, background, color, color_dark, top_offset, side_offset, bottom_offset,
                           font_standard)) \
        .add_app(EnvironmentApp(update_display, ENVIRONMENT_DATA_PROVIDER,
                                resolution, background, color, color_dark, top_offset, side_offset, bottom_offset,
                                font_standard)) \
        .add_app(RadioApp(resolution, background, color, color_dark, top_offset, side_offset, bottom_offset,
                          font_standard)) \
        .add_app(DebugApp(resolution, color, color_dark)) \
        .add_app(ClockApp(update_display, resolution, color)) \
        .add_app(MapApp(update_display, LOCATION_PROVIDER, OSMTileProvider(background, color, font_standard),
                        resolution, background, color, color_dark, top_offset, side_offset, bottom_offset,
                        font_standard
                        )
                 )

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
