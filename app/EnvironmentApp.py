from app.App import SelfUpdatingApp
from data.EnvironmentDataProvider import EnvironmentDataProvider, EnvironmentData
from PIL import Image, ImageDraw, ImageFont
from typing import Callable, Any
import os


class EnvironmentApp(SelfUpdatingApp):

    def __init__(self, draw_callback: Callable[[Any], None],
                 data_provider: EnvironmentDataProvider, resolution: tuple[int, int],
                 background: tuple[int, int, int], color: tuple[int, int, int], color_dark: tuple[int, int, int],
                 app_top_offset: int, app_side_offset: int, app_bottom_offset: int,
                 font_standard: ImageFont.FreeTypeFont):
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
        self.__data: EnvironmentData | None = None
        try:
            self.__data = self.__data_provider.get_environment_data()
        except TimeoutError:
            pass

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
        try:
            self.__data = self.__data_provider.get_environment_data()
        except TimeoutError:
            self.__data = None
        self.__draw_callback(**self.__draw_callback_kwargs)

    def draw(self, image: Image.Image, partial=False) -> tuple[Image.Image, int, int]:
        draw = ImageDraw.Draw(image)
        width, height = self.__resolution
        icon_gap = 10
        left_top = ((width - self.__t_icon.width - self.__p_icon.width - self.__h_icon.width - 2 * icon_gap) // 2,
                    self.__app_top_offset + 50)

        temperature_xy = left_top
        pressure_xy = (temperature_xy[0] + self.__t_icon.width + icon_gap, temperature_xy[1])
        humidity_xy = (pressure_xy[0] + self.__p_icon.width + icon_gap, pressure_xy[1])

        # only drawn once
        if not partial:
            draw.bitmap(temperature_xy, self.__t_icon, fill=self.__color)
            draw.bitmap(pressure_xy, self.__p_icon, fill=self.__color)
            draw.bitmap(humidity_xy, self.__h_icon, fill=self.__color)

        draw_area_left_top = (left_top[0],
                              min(temperature_xy[1] + self.__t_icon.height,
                              pressure_xy[1] + self.__p_icon.height,
                              humidity_xy[1] + self.__h_icon.height))

        # format with two decimals, and seven characters in total (adds whitespaces on the left to fill)
        t_text = f'{self.__data.temperature:.2f} °C' if self.__data is not None else '? °C'
        p_text = f'{self.__data.pressure:.2f} hPa' if self.__data is not None else '? hPa'
        h_text = f'{self.__data.humidity:.2%}' if self.__data is not None else '?%'
        _, _, t_text_width, t_text_height = self.__font.getbbox(t_text)
        _, _, p_text_width, p_text_height = self.__font.getbbox(p_text)
        _, _, h_text_width, h_text_height = self.__font.getbbox(h_text)
        draw.text((temperature_xy[0] + (self.__t_icon.width - t_text_width) // 2,
                   temperature_xy[1] + self.__t_icon.height + icon_gap),
                  t_text, self.__color, font=self.__font)
        draw.text((pressure_xy[0] + (self.__p_icon.width - p_text_width) // 2,
                   pressure_xy[1] + self.__p_icon.height + icon_gap),
                  p_text, self.__color, font=self.__font)
        draw.text((humidity_xy[0] + (self.__h_icon.width - h_text_width) // 2,
                   humidity_xy[1] + self.__h_icon.height + icon_gap),
                  h_text, self.__color, font=self.__font)

        if partial:
            right_bottom = (humidity_xy[0] + (self.__h_icon.width - h_text_width) // 2 + h_text_width,
                            draw_area_left_top[1] + icon_gap + max(t_text_height, p_text_height, h_text_height))
            return image.crop(draw_area_left_top + right_bottom), *draw_area_left_top  # noqa (unpacking type check fail)
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
