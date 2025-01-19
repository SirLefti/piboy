import time
from datetime import datetime
from typing import Any, Callable, Generator, Self

from injector import Injector, Module, provider, singleton
from PIL import Image, ImageDraw

import environment
from app.App import App
from app.ClockApp import ClockApp
from app.DebugApp import DebugApp
from app.EnvironmentApp import EnvironmentApp
from app.FileManagerApp import FileManagerApp
from app.MapApp import MapApp
from app.RadioApp import RadioApp
from app.UpdateApp import UpdateApp
from core import resources
from core.data import ConnectionStatus, DeviceStatus
from data.BatteryStatusProvider import BatteryStatusProvider
from data.EnvironmentDataProvider import EnvironmentDataProvider
from data.LocationProvider import LocationProvider
from data.NetworkStatusProvider import NetworkStatusProvider
from data.OSMTileProvider import OSMTileProvider
from data.TileProvider import TileProvider
from environment import AppConfig, Environment
from interaction.Display import Display
from interaction.Input import Input
from interaction.UnifiedInteraction import UnifiedInteraction


class AppState:

    __bit = 0

    def __init__(self, e: Environment, network_status_provider: NetworkStatusProvider,
                 location_provider: LocationProvider, battery_status_provider: BatteryStatusProvider,
                 environment_data_provider: EnvironmentDataProvider):
        self.__environment = e
        self.__network_status_provider = network_status_provider
        self.__location_provider = location_provider
        self.__battery_status_provider = battery_status_provider
        self.__environment_data_provider = environment_data_provider
        self.__image_buffer = self.__init_buffer()
        self.__apps: list[App] = []
        self.__active_app = 0

    def __init_buffer(self) -> Image.Image:
        return Image.new('RGB', self.__environment.app_config.resolution, self.__environment.app_config.background)

    def __tick(self):
        self.__bit ^= 1

    def clear_buffer(self) -> Image.Image:
        self.__image_buffer = self.__init_buffer()
        return self.__image_buffer

    def add_app(self, app: App) -> Self:
        self.__apps.append(app)
        return self

    @property
    def __app_anchor(self) -> tuple[int, int]:
        return self.__environment.app_config.app_side_offset, self.__environment.app_config.app_top_offset

    @property
    def __app_bbox(self) -> tuple[int, int, int, int]:
        return (self.__environment.app_config.app_side_offset,
                self.__environment.app_config.app_top_offset,
                self.__environment.app_config.width - self.__environment.app_config.app_side_offset,
                self.__environment.app_config.height - self.__environment.app_config.app_bottom_offset)

    @property
    def tick(self) -> int:
        return self.__bit

    @property
    def environment(self) -> Environment:
        return self.__environment

    @property
    def network_status_provider(self) -> NetworkStatusProvider:
        return self.__network_status_provider

    @property
    def location_provider(self) -> LocationProvider:
        return self.__location_provider

    @property
    def battery_status_provider(self) -> BatteryStatusProvider:
        return self.__battery_status_provider

    @property
    def environment_data_provider(self) -> EnvironmentDataProvider:
        return self.__environment_data_provider

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

    def watch_function(self, display: Display):
        while True:
            now = datetime.now()
            # wait for next second
            time.sleep(1.0 - now.microsecond / 1000000.0)

            # draw the complete footer to remove existing clock display
            image, x0, y0 = draw_footer(self.image_buffer, self)
            display.show(image, x0, y0)
            self.__tick()

    def update_display(self, display: Display, partial=False):
        """Draw call that handles the complete cycle of drawing a new image to the display."""
        image = self.clear_buffer()
        if not partial:
            for patch, x0, y0 in draw_base(image, self):
                display.show(patch, x0, y0)

        x_offset, y_offset = self.__app_anchor
        for patch, x0, y0 in self.active_app.draw(image.crop(self.__app_bbox), partial):
            display.show(patch, x0 + x_offset, y0 + y_offset)

    def on_key_left(self, display: Display):
        self.active_app.on_key_left()
        self.update_display(display, partial=True)

    def on_key_right(self, display: Display):
        self.active_app.on_key_right()
        self.update_display(display, partial=True)

    def on_key_up(self, display: Display):
        self.active_app.on_key_up()
        self.update_display(display, partial=True)

    def on_key_down(self, display: Display):
        self.active_app.on_key_down()
        self.update_display(display, partial=True)

    def on_key_a(self, display: Display):
        self.active_app.on_key_a()
        self.update_display(display, partial=True)

    def on_key_b(self, display: Display):
        self.active_app.on_key_b()
        self.update_display(display, partial=True)

    def on_rotary_increase(self, display: Display):
        self.active_app.on_app_leave()
        self.next_app()
        self.active_app.on_app_enter()
        self.update_display(display, partial=False)

    def on_rotary_decrease(self, display: Display):
        self.active_app.on_app_leave()
        self.previous_app()
        self.active_app.on_app_enter()
        self.update_display(display, partial=False)


class AppModule(Module):

    __unified_instance: UnifiedInteraction | None = None

    def register_external_tk_interaction(self, tk_instance: UnifiedInteraction):
        self.__unified_instance = tk_instance

    @staticmethod
    def __create_tk_interaction(state: AppState, app_config: AppConfig) -> UnifiedInteraction:
        from interaction.TkInteraction import TkInteraction
        return TkInteraction(state.on_key_left, state.on_key_right, state.on_key_up, state.on_key_down,
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
    def provide_app_state(self, e: Environment, network_status_provider: NetworkStatusProvider,
                          location_provider: LocationProvider,
                          battery_status_provider: BatteryStatusProvider,
                          environment_data_provider: EnvironmentDataProvider) -> AppState:
        return AppState(e, network_status_provider, location_provider, battery_status_provider,
                        environment_data_provider)

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
    def provide_network_status_service(self, e: Environment) -> NetworkStatusProvider:
        if e.dev_mode:
            from data.FakeNetworkStatusProvider import FakeNetworkStatusProvider
            return FakeNetworkStatusProvider()
        else:
            from data.NetworkManagerStatusProvider import NetworkManagerStatusProvider
            return NetworkManagerStatusProvider()

    @singleton
    @provider
    def provide_battery_status_service(self, e: Environment) -> BatteryStatusProvider:
        if e.dev_mode:
            from data.FakeBatteryStatusProvider import FakeBatteryStatusProvider
            return FakeBatteryStatusProvider()
        else:
            from data.ADS1115BatteryStatusProvider import ADS1115BatteryStatusProvider
            return ADS1115BatteryStatusProvider(e.adc_config.port, e.adc_config.address)

    @singleton
    @provider
    def provide_draw_callback(self, state: AppState, display: Display) -> Callable[[bool], None]:
        return lambda partial: state.update_display(display, partial)

    @singleton
    @provider
    def provide_display(self, e: Environment, state: AppState) -> Display:
        if e.dev_mode:
            if self.__unified_instance is None:
                self.__unified_instance = self.__create_tk_interaction(state, e.app_config)
            return self.__unified_instance
        else:
            from interaction.ILI9486Display import ILI9486Display

            spi_device_config = e.display_config.display_device
            return ILI9486Display((spi_device_config.bus, spi_device_config.device),
                                  e.display_config.dc_pin, e.display_config.rst_pin, e.display_config.flip_display)

    @singleton
    @provider
    def provide_input(self, e: Environment, state: AppState, display: Display) -> Input:
        if e.dev_mode:
            if self.__unified_instance is None:
                self.__unified_instance = self.__create_tk_interaction(state, e.app_config)
            return self.__unified_instance
        else:
            from interaction.GPIOInput import GPIOInput
            from interaction.ILI9486Display import ILI9486Display

            # make sure that display is ILI9486Interface to call the reset function, should be always true
            switch_function = display.reset if isinstance(display, ILI9486Display) else lambda: None

            return GPIOInput(e.keypad_config.left_pin, e.keypad_config.right_pin,
                             e.keypad_config.up_pin, e.keypad_config.down_pin,
                             e.keypad_config.a_pin, e.keypad_config.b_pin,
                             e.rotary_config.rotary_device, e.rotary_config.sw_pin,
                             lambda: state.on_key_left(display), lambda: state.on_key_right(display),
                             lambda: state.on_key_up(display), lambda: state.on_key_down(display),
                             lambda: state.on_key_a(display), lambda: state.on_key_b(display),
                             lambda: state.on_rotary_increase(display), lambda: state.on_rotary_decrease(display),
                             switch_function)


def draw_footer(image: Image.Image, state: AppState) -> tuple[Image.Image, int, int]:
    width, height = state.environment.app_config.resolution
    footer_height = 20  # height of the footer
    footer_bottom_offset = 3  # spacing to the bottom
    icon_padding = 3 # padding between status icons
    footer_side_offset = state.environment.app_config.app_side_offset  # spacing to the sides
    font = state.environment.app_config.font_header
    draw = ImageDraw.Draw(image)

    start = (footer_side_offset, height - footer_height - footer_bottom_offset)
    end = (width - footer_side_offset - 1, height - footer_bottom_offset - 1)
    cursor_x, cursor_y = start
    connection_status_color = {
        ConnectionStatus.CONNECTED: state.environment.app_config.accent,
        ConnectionStatus.DISCONNECTED: state.environment.app_config.accent if state.tick else state.environment.app_config.background
    }
    device_status_color = {
        DeviceStatus.OPERATIONAL: state.environment.app_config.accent,
        DeviceStatus.NO_DATA: state.environment.app_config.accent if state.tick else state.environment.app_config.background,
        DeviceStatus.UNAVAILABLE: state.environment.app_config.background
    }

    # reset area
    draw.rectangle(start + end, fill=state.environment.app_config.accent_dark)

    # draw network status
    nw_status_padding = (footer_height - resources.network_icon.height) // 2
    nw_status_color = connection_status_color[state.network_status_provider.get_connection_status()]
    draw.bitmap((cursor_x + icon_padding, cursor_y + nw_status_padding), resources.network_icon, fill=nw_status_color)
    cursor_x += resources.network_icon.width + icon_padding

    # draw gps status
    gps_status_padding = (footer_height - resources.gps_icon.height) // 2
    gps_status_color = device_status_color[state.location_provider.get_device_status()]
    draw.bitmap((cursor_x + icon_padding, cursor_y + gps_status_padding), resources.gps_icon, fill=gps_status_color)
    cursor_x += resources.gps_icon.width + icon_padding

    # draw battery status
    state_of_charge_str = f'{state.battery_status_provider.get_state_of_charge():.0%}'
    _, _, text_width, text_height = font.getbbox(state_of_charge_str)
    text_padding = (footer_height - text_height) // 2
    draw.text((cursor_x + icon_padding, cursor_y + text_padding), state_of_charge_str,
              state.environment.app_config.accent, font=font)
    cursor_x += text_width

    # draw time
    date_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    _, _, text_width, text_height = font.getbbox(date_str)
    text_padding = (footer_height - text_height) // 2
    draw.text((width - footer_side_offset - text_padding - text_width, cursor_y + text_padding), date_str,
              state.environment.app_config.accent, font=font)

    x0, y0 = start
    end = end[0] + 1, end[1] + 1
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
    end = (width - header_side_offset - 1, header_top_offset)
    draw.line(start + end, fill=color_accent)
    start = end
    end = (width - header_side_offset - 1, header_top_offset + vertical_line)
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


def draw_base(image: Image.Image, state: AppState) -> Generator[tuple[Image.Image, int, int], Any, None]:
    yield draw_header(image, state)
    yield draw_footer(image, state)


def is_raspberry_pi() -> bool:
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as model_info:
            return 'Raspberry Pi' in model_info.read()
    except FileNotFoundError:
        return False


if __name__ == '__main__':
    injector = Injector([AppModule()])
    app_state = injector.get(AppState)

    DISPLAY = injector.get(Display)
    INPUT = injector.get(Input)

    app_state.add_app(injector.get(FileManagerApp)) \
        .add_app(injector.get(UpdateApp)) \
        .add_app(injector.get(EnvironmentApp)) \
        .add_app(injector.get(RadioApp)) \
        .add_app(injector.get(DebugApp)) \
        .add_app(injector.get(ClockApp)) \
        .add_app(injector.get(MapApp))

    # initially draw the empty buffer to initialize all pixels on the hardware module
    DISPLAY.show(app_state.image_buffer, 0, 0)
    # then continue with the initial draw call
    app_state.update_display(DISPLAY)
    app_state.active_app.on_app_enter()

    try:
        # blocking function that updates the clock
        app_state.watch_function(DISPLAY)
    except KeyboardInterrupt:
        pass
    finally:
        DISPLAY.close()
        INPUT.close()
