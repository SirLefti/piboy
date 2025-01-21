from typing import Any, Generator, Iterable, Callable

from injector import inject
from PIL import Image, ImageDraw

from app.App import SelfUpdatingApp
from core.data import DeviceStatus
from core.decorator import override
from data.BatteryStatusProvider import BatteryStatusProvider
from data.EnvironmentDataProvider import EnvironmentDataProvider
from data.LocationProvider import LocationProvider
from environment import AppConfig


class DebugApp(SelfUpdatingApp):

    INDEX_LEFT = 0
    INDEX_RIGHT = 1
    INDEX_UP = 2
    INDEX_DOWN = 3
    INDEX_A = 4
    INDEX_B = 5

    @inject
    def __init__(self, app_config: AppConfig, location_provider: LocationProvider,
                 environment_data_provider: EnvironmentDataProvider, battery_status_provider: BatteryStatusProvider,
                 update_callback: Callable[[bool], None]):
        super().__init__(self.__draw_callback_internal)
        self.__draw_callback = update_callback
        self.__draw_callback_kwargs = {'partial': True}

        # left, right, up, down, a, b
        self.__key_state = [False, False, False, False, False, False]
        self.__last_key_state = [False, False, False, False, False, False]
        # gps, env, adc
        self.__device_state = [DeviceStatus.UNAVAILABLE, DeviceStatus.UNAVAILABLE, DeviceStatus.UNAVAILABLE]
        self.__last_device_state = [DeviceStatus.UNAVAILABLE, DeviceStatus.UNAVAILABLE, DeviceStatus.UNAVAILABLE]

        self.__font = app_config.font_standard
        self.__app_size = app_config.app_size
        self.__color = app_config.accent
        self.__color_dark = app_config.accent_dark

        self.__devices = {
            'GPS': location_provider,
            'ENV': environment_data_provider,
            'ADC': battery_status_provider
        }

    @property
    @override
    def refresh_time(self) -> float:
        return 10

    @property
    @override
    def title(self) -> str:
        return 'DBG'

    @staticmethod
    def __get_bbox(coordinates: Iterable[tuple[int, int]]) -> tuple[int, int, int, int]:
        max_x = max(coordinates, key=lambda e: e[0])[0]
        max_y = max(coordinates, key=lambda e: e[1])[1]
        min_x = min(coordinates, key=lambda e: e[0])[0]
        min_y = min(coordinates, key=lambda e: e[1])[1]
        # expanding by +1 to include all drawn pixels by cropping
        return min_x, min_y, max_x + 1, max_y + 1

    def __draw_callback_internal(self):
        self.__update_data()
        self.__draw_callback(**self.__draw_callback_kwargs)

    def __update_data(self):
        self.__last_device_state = self.__device_state
        self.__device_state = [d.get_device_status() for d in self.__devices.values()]

    @override
    def draw(self, image: Image.Image, partial=False) -> Generator[tuple[Image.Image, int, int], Any, None]:
        width, height = self.__app_size
        center_x, center_y = int(width / 4), int(height / 2)
        # center of right side
        r_center_x = center_x * 3

        device_spacing = 20

        dpad_offset = 40
        dpad_spacing = 20
        action_offset = 40
        action_spacing = 20
        button_size = 30

        draw = ImageDraw.Draw(image)

        cursor = (10, 10)
        for index, device_name in enumerate(self.__devices):
            if not partial or self.__device_state[index] != self.__last_device_state[index]:
                last_text = f'{device_name}: {self.__last_device_state[index]}'.replace('DeviceStatus.', '')
                last_text_width, last_text_height = self.__font.getbbox(last_text)[2:]

                text = f'{device_name}: {self.__device_state[index]}'.replace('DeviceStatus.', '')
                text_width, text_height = self.__font.getbbox(text)[2:]
                draw.text(cursor, text, self.__color, font=self.__font)

                bbox = (cursor[0], cursor[1], cursor[0]
                        + max(last_text_width, text_width), cursor[1] + max(last_text_height, text_height))
                yield image.crop(bbox), *cursor
            # always move the cursor, even if we did not perform a draw call, because it is already there
            cursor = (cursor[0], cursor[1] + device_spacing)

        draw_left = not partial or self.__key_state[self.INDEX_LEFT] != self.__last_key_state[self.INDEX_LEFT]
        draw_right = not partial or self.__key_state[self.INDEX_RIGHT] != self.__last_key_state[self.INDEX_RIGHT]
        draw_up = not partial or self.__key_state[self.INDEX_UP] != self.__last_key_state[self.INDEX_UP]
        draw_down = not partial or self.__key_state[self.INDEX_DOWN] != self.__last_key_state[self.INDEX_DOWN]
        draw_a = not partial or self.__key_state[self.INDEX_A] != self.__last_key_state[self.INDEX_A]
        draw_b = not partial or self.__key_state[self.INDEX_B] != self.__last_key_state[self.INDEX_B]

        if draw_left:
            points_left = [
                (r_center_x - dpad_offset - dpad_spacing, center_y - button_size // 2),
                (r_center_x - dpad_offset - dpad_spacing, center_y + button_size // 2),
                (r_center_x - dpad_offset - dpad_spacing - button_size, center_y)
            ]
            draw.polygon(points_left, fill=(self.__color if self.__key_state[self.INDEX_LEFT] else self.__color_dark))
            bbox = self.__get_bbox(points_left)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_right:
            points_right = [
                (r_center_x - dpad_offset + dpad_spacing, center_y - button_size // 2),
                (r_center_x - dpad_offset + dpad_spacing, center_y + button_size // 2),
                (r_center_x - dpad_offset + dpad_spacing + button_size, center_y)
            ]
            draw.polygon(points_right, fill=(self.__color if self.__key_state[self.INDEX_RIGHT] else self.__color_dark))
            bbox = self.__get_bbox(points_right)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_up:
            points_up = [
                (r_center_x - dpad_offset - button_size // 2, center_y - dpad_spacing),
                (r_center_x - dpad_offset + button_size // 2, center_y - dpad_spacing),
                (r_center_x - dpad_offset, center_y - dpad_spacing - button_size)
            ]
            draw.polygon(points_up, fill=(self.__color if self.__key_state[self.INDEX_UP] else self.__color_dark))
            bbox = self.__get_bbox(points_up)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_down:
            points_down = [
                (r_center_x - dpad_offset - button_size // 2, center_y + dpad_spacing),
                (r_center_x - dpad_offset + button_size // 2, center_y + dpad_spacing),
                (r_center_x - dpad_offset, center_y + dpad_spacing + button_size)
            ]
            draw.polygon(points_down, fill=(self.__color if self.__key_state[self.INDEX_DOWN] else self.__color_dark))
            bbox = self.__get_bbox(points_down)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_a:
            points_a = ((r_center_x + action_offset - button_size // 2, center_y - button_size - action_spacing // 2),
                        (r_center_x + action_offset + button_size // 2, center_y - action_spacing // 2))
            draw.rectangle(points_a, fill=(self.__color if self.__key_state[self.INDEX_A] else self.__color_dark))
            bbox = self.__get_bbox(points_a)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_b:
            points_b = ((r_center_x + action_offset - button_size // 2, center_y + action_spacing // 2),
                        (r_center_x + action_offset + button_size // 2, center_y + button_size + action_spacing // 2))
            draw.rectangle(points_b, fill=(self.__color if self.__key_state[self.INDEX_B] else self.__color_dark))
            bbox = self.__get_bbox(points_b)
            yield image.crop(bbox), bbox[0], bbox[1]

    @override
    def on_key_left(self):
        self.__last_key_state = self.__key_state
        self.__key_state = [e == self.INDEX_LEFT for e in range(6)]

    @override
    def on_key_right(self):
        self.__last_key_state = self.__key_state
        self.__key_state = [e == self.INDEX_RIGHT for e in range(6)]

    @override
    def on_key_up(self):
        self.__last_key_state = self.__key_state
        self.__key_state = self.__key_state = [e == self.INDEX_UP for e in range(6)]

    @override
    def on_key_down(self):
        self.__last_key_state = self.__key_state
        self.__key_state = self.__key_state = [e == self.INDEX_DOWN for e in range(6)]

    @override
    def on_key_a(self):
        self.__last_key_state = self.__key_state
        self.__key_state = self.__key_state = [e == self.INDEX_A for e in range(6)]

    @override
    def on_key_b(self):
        self.__last_key_state = self.__key_state
        self.__key_state = self.__key_state = [e == self.INDEX_B for e in range(6)]

    @override
    def on_app_enter(self):
        super().on_app_enter()
        self.__update_data()

    @override
    def on_app_leave(self):
        self.__key_state = [False, False, False, False, False, False]
        self.__last_key_state = [False, False, False, False, False, False]
