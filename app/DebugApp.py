from typing import Any, Generator, Iterable

from injector import inject
from PIL import Image, ImageDraw

from app.App import App
from core.decorator import override
from environment import AppConfig


class DebugApp(App):
    
    INDEX_LEFT = 0
    INDEX_RIGHT = 1
    INDEX_UP = 2
    INDEX_DOWN = 3
    INDEX_A = 4
    INDEX_B = 5

    @inject
    def __init__(self, app_config: AppConfig):
        # left, right, up, down, a, b
        self.__state = [False, False, False, False, False, False]
        self.__last_state = [False, False, False, False, False, False]
        self.__app_size = app_config.app_size
        self.__color = app_config.accent
        self.__color_dark = app_config.accent_dark

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

    @override
    def draw(self, image: Image.Image, partial=False) -> Generator[tuple[Image.Image, int, int], Any, None]:
        width, height = self.__app_size
        center_x, center_y = int(width / 2), int(height / 2)

        dpad_offset = 40
        dpad_spacing = 20
        action_offset = 40
        action_spacing = 20
        button_size = 30

        draw = ImageDraw.Draw(image)

        draw_left = not partial or self.__state[self.INDEX_LEFT] != self.__last_state[self.INDEX_LEFT]
        draw_right = not partial or self.__state[self.INDEX_RIGHT] != self.__last_state[self.INDEX_RIGHT]
        draw_up = not partial or self.__state[self.INDEX_UP] != self.__last_state[self.INDEX_UP]
        draw_down = not partial or self.__state[self.INDEX_DOWN] != self.__last_state[self.INDEX_DOWN]
        draw_a = not partial or self.__state[self.INDEX_A] != self.__last_state[self.INDEX_A]
        draw_b = not partial or self.__state[self.INDEX_B] != self.__last_state[self.INDEX_B]

        if draw_left:
            points_left = [
                (center_x - dpad_offset - dpad_spacing, center_y - button_size // 2),
                (center_x - dpad_offset - dpad_spacing, center_y + button_size // 2),
                (center_x - dpad_offset - dpad_spacing - button_size, center_y)
            ]
            draw.polygon(points_left, fill=(self.__color if self.__state[self.INDEX_LEFT] else self.__color_dark))
            bbox = self.__get_bbox(points_left)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_right:
            points_right = [
                (center_x - dpad_offset + dpad_spacing, center_y - button_size // 2),
                (center_x - dpad_offset + dpad_spacing, center_y + button_size // 2),
                (center_x - dpad_offset + dpad_spacing + button_size, center_y)
            ]
            draw.polygon(points_right, fill=(self.__color if self.__state[self.INDEX_RIGHT] else self.__color_dark))
            bbox = self.__get_bbox(points_right)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_up:
            points_up = [
                (center_x - dpad_offset - button_size // 2, center_y - dpad_spacing),
                (center_x - dpad_offset + button_size // 2, center_y - dpad_spacing),
                (center_x - dpad_offset, center_y - dpad_spacing - button_size)
            ]
            draw.polygon(points_up, fill=(self.__color if self.__state[self.INDEX_UP] else self.__color_dark))
            bbox = self.__get_bbox(points_up)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_down:
            points_down = [
                (center_x - dpad_offset - button_size // 2, center_y + dpad_spacing),
                (center_x - dpad_offset + button_size // 2, center_y + dpad_spacing),
                (center_x - dpad_offset, center_y + dpad_spacing + button_size)
            ]
            draw.polygon(points_down, fill=(self.__color if self.__state[self.INDEX_DOWN] else self.__color_dark))
            bbox = self.__get_bbox(points_down)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_a:
            points_a = ((center_x + action_offset - button_size // 2, center_y - button_size - action_spacing // 2),
                        (center_x + action_offset + button_size // 2, center_y - action_spacing // 2))
            draw.rectangle(points_a, fill=(self.__color if self.__state[self.INDEX_A] else self.__color_dark))
            bbox = self.__get_bbox(points_a)
            yield image.crop(bbox), bbox[0], bbox[1]

        if draw_b:
            points_b = ((center_x + action_offset - button_size // 2, center_y + action_spacing // 2),
                        (center_x + action_offset + button_size // 2, center_y + button_size + action_spacing // 2))
            draw.rectangle(points_b, fill=(self.__color if self.__state[self.INDEX_B] else self.__color_dark))
            bbox = self.__get_bbox(points_b)
            yield image.crop(bbox), bbox[0], bbox[1]

    @override
    def on_key_left(self):
        self.__last_state = self.__state
        self.__state = [True, False, False, False, False, False]

    @override
    def on_key_right(self):
        self.__last_state = self.__state
        self.__state = [False, True, False, False, False, False]

    @override
    def on_key_up(self):
        self.__last_state = self.__state
        self.__state = [False, False, True, False, False, False]

    @override
    def on_key_down(self):
        self.__last_state = self.__state
        self.__state = [False, False, False, True, False, False]

    @override
    def on_key_a(self):
        self.__last_state = self.__state
        self.__state = [False, False, False, False, True, False]

    @override
    def on_key_b(self):
        self.__last_state = self.__state
        self.__state = [False, False, False, False, False, True]

    @override
    def on_app_leave(self):
        self.__state = [False, False, False, False, False, False]
        self.__last_state = [False, False, False, False, False, False]
