from app.App import SelfUpdatingApp
from data.EnvironmentDataProvider import EnvironmentDataProvider, EnvironmentData
from PIL import Image, ImageDraw, ImageFont
from typing import Callable, Any, Tuple
import os


class EnvironmentApp(SelfUpdatingApp):

    def __init__(self, draw_callback: Callable[[Any], None],
                 data_provider: EnvironmentDataProvider, resolution: Tuple[int, int],
                 background: Tuple[int, int, int], color: Tuple[int, int, int], color_dark: Tuple[int, int, int],
                 app_top_offset: int, app_side_offset: int, app_bottom_offset: int, font_standard: ImageFont):
        super().__init__(self.__update_data)
        self.__resolution = resolution
        self.__background = background
        self.__color = color
        self.__color_dark = color_dark
        self.__app_top_offset = app_top_offset
        self.__app_side_offset = app_side_offset
        self.__app_bottom_offset = app_bottom_offset
        self.__font = font_standard

        self.__draw_callback = draw_callback
        self.__draw_callback_kwargs = {'partial': True}
        self.__data_provider = data_provider
        self.__data: EnvironmentData = self.__data_provider.get_environment_data()

        resources_path = 'resources'
        self.__t_icon = Image.open(os.path.join(resources_path, 'temperature.png')).convert('1')
        self.__p_icon = Image.open(os.path.join(resources_path, 'pressure.png')).convert('1')
        self.__h_icon = Image.open(os.path.join(resources_path, 'humidity.png')).convert('1')

    @property
    def refresh_time(self) -> float:
        return 10

    @property
    def title(self) -> str:
        return 'ENV'

    def __update_data(self):
        self.__data = self.__data_provider.get_environment_data()
        self.__draw_callback(**self.__draw_callback_kwargs)

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        draw = ImageDraw.Draw(image)
        width, height = self.__resolution
        icon_gap = 5
        left_top = (self.__app_side_offset + 150, self.__app_top_offset + 50)

        temperature_xy = left_top
        pressure_xy = (temperature_xy[0], temperature_xy[1] + self.__t_icon.height)
        humidity_xy = (pressure_xy[0], pressure_xy[1] + self.__p_icon.height)

        # only drawn once
        if not partial:
            draw.bitmap(temperature_xy, self.__t_icon, fill=self.__color)
            draw.bitmap(pressure_xy, self.__p_icon, fill=self.__color)
            draw.bitmap(humidity_xy, self.__h_icon, fill=self.__color)

        draw_area_left_top = (min(temperature_xy[0] + self.__t_icon.width,
                              pressure_xy[0] + self.__p_icon.width,
                              humidity_xy[0] + self.__h_icon.width), left_top[1])

        # format with two decimals, and seven characters in total (adds whitespaces on the left to fill)
        draw.text((temperature_xy[0] + self.__t_icon.width + icon_gap, temperature_xy[1]),
                  f'{self.__data.temperature:.2f} °C', self.__color, font=self.__font)
        draw.text((pressure_xy[0] + self.__p_icon.width + icon_gap, pressure_xy[1]),
                  f'{self.__data.pressure:.2f} hPa', self.__color, font=self.__font)
        draw.text((humidity_xy[0] + self.__h_icon.width + icon_gap, humidity_xy[1]),
                  f'{self.__data.humidity:.2%}', self.__color, font=self.__font)

        if partial:
            right_bottom = width - self.__app_side_offset, humidity_xy[1] + self.__h_icon.height
            return image.crop(draw_area_left_top + right_bottom), *draw_area_left_top
        else:
            return image, 0, 0

    def on_key_left(self):
        pass

    def on_key_right(self):
        pass

    def on_key_up(self):
        pass

    def on_key_down(self):
        pass

    def on_key_a(self):
        pass

    def on_key_b(self):
        pass
