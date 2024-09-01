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
from data.TileProvider import TileProvider
from data.OSMTileProvider import OSMTileProvider
from interface.Interface import Interface
from interface.Input import Input
from interface.UnifiedInteraction import UnifiedInteraction
from typing import Callable
from PIL import Image, ImageDraw
from datetime import datetime
from environment import Environment, AppConfig
from injector import Injector, Module, provider, singleton
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


class AppModule(Module):

    __unified_instance: UnifiedInteraction | None = None

    def register_external_tk_interface(self, tk_instance: UnifiedInteraction):
        self.__unified_instance = tk_instance

    @staticmethod
    def __create_tk_interface(state: AppState, app_config: AppConfig) -> UnifiedInteraction:
        from interface.TkInterface import TkInterface
        return TkInterface(state.on_key_left, state.on_key_right, state.on_key_up, state.on_key_down,
                           state.on_key_a, state.on_key_b, state.on_rotary_increase, state.on_rotary_decrease,
                           lambda _: None, app_config.resolution, app_config.background, app_config.accent_dark)

    @singleton
    @provider
    def provide_environment(self) -> Environment:
        environment.configure()
        try:
            return environment.load()
        except FileNotFoundError:
            e = Environment()
            e.dev_mode = not is_raspberry_pi()
            environment.save(e)
            return e

    @singleton
    @provider
    def provide_app_config(self, e: Environment) -> AppConfig:
        return e.app_config

    @singleton
    @provider
    def provide_app_state(self, e: Environment) -> AppState:
        return AppState(e)

    @singleton
    @provider
    def provide_environment_data_service(self, e: Environment) -> EnvironmentDataProvider:
        if e.dev_mode:
            from data.FakeEnvironmentDataProvider import FakeEnvironmentDataProvider
            return FakeEnvironmentDataProvider()
        else:
            from data.BME280EnvironmentDataProvider import BME280EnvironmentDataProvider
            return BME280EnvironmentDataProvider(e.env_sensor_config.port, e.env_sensor_config.address)

    @singleton
    @provider
    def provide_location_service(self, e: Environment) -> LocationProvider:
        if e.dev_mode:
            from data.IPLocationProvider import IPLocationProvider
            return IPLocationProvider(apply_inaccuracy=True)
        else:
            from data.SerialGPSLocationProvider import SerialGPSLocationProvider
            return SerialGPSLocationProvider(e.gps_module_config.port, baudrate=e.gps_module_config.baudrate)

    @singleton
    @provider
    def provide_tile_service(self, e: Environment) -> TileProvider:
        return OSMTileProvider(e.app_config.background, e.app_config.accent, e.app_config.font_standard)


    @singleton
    @provider
    def provide_draw_callback(self, state: AppState, interface: Interface) -> Callable[[bool], None]:
        return lambda partial: state.update_display(interface, partial)


    @singleton
    @provider
    def provide_interface(self, e: Environment, state: AppState) -> Interface:
        if e.dev_mode:
            if self.__unified_instance is None:
                self.__unified_instance = self.__create_tk_interface(state, e.app_config)
            return self.__unified_instance
        else:
            from interface.ILI9486Interface import ILI9486Interface

            spi_device_config = e.display_config.display_device
            return ILI9486Interface((spi_device_config.bus, spi_device_config.device),
                                    e.display_config.dc_pin, e.display_config.rst_pin, e.display_config.flip_display)

    @singleton
    @provider
    def provide_input(self, e: Environment, state: AppState, interface: Interface) -> Input:
        if e.dev_mode:
            if self.__unified_instance is None:
                self.__unified_instance = self.__create_tk_interface(state, e.app_config)
            return self.__unified_instance
        else:
            from interface.GPIOInput import GPIOInput
            from interface.ILI9486Interface import ILI9486Interface

            # make sure that interface is ILI9486Interface to call the reset function, should be always true
            switch_function = interface.reset if isinstance(interface, ILI9486Interface) else lambda: None

            return GPIOInput(e.keypad_config.left_pin, e.keypad_config.right_pin,
                             e.keypad_config.up_pin, e.keypad_config.down_pin,
                             e.keypad_config.a_pin, e.keypad_config.b_pin,
                             e.rotary_config.rotary_device, e.rotary_config.sw_pin,
                             lambda: state.on_key_left(interface), lambda: state.on_key_right(interface),
                             lambda: state.on_key_up(interface), lambda: state.on_key_down(interface),
                             lambda: state.on_key_a(interface), lambda: state.on_key_b(interface),
                             lambda: state.on_rotary_increase(interface), lambda: state.on_rotary_decrease(interface),
                             switch_function)


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
    app_text_width = sum(int(font.getbbox(app.title)[2]) for app in state.apps) + (len(state.apps) - 1) * app_spacing
    cursor = header_side_offset + (max_text_width - app_text_width) // 2
    for app in state.apps:
        _, _, text_width, text_height = map(int, font.getbbox(app.title))
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


if __name__ == '__main__':
    INTERFACE: Interface
    INPUT: Input

    injector = Injector([AppModule()])

    env = injector.get(Environment)
    app_state = injector.get(AppState)

    INTERFACE = injector.get(Interface)
    INPUT = injector.get(Input)

    draw_callback = lambda partial : app_state.update_display(INTERFACE, partial)
    app_state.add_app(injector.get(FileManagerApp)) \
        .add_app(injector.get(UpdateApp)) \
        .add_app(injector.get(EnvironmentApp)) \
        .add_app(injector.get(RadioApp)) \
        .add_app(injector.get(DebugApp)) \
        .add_app(injector.get(ClockApp)) \
        .add_app(injector.get(MapApp))

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
