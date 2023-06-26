from app.App import App
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Collection
import pyaudio
import wave
import os


class RadioApp(App):
    __CONTROL_PADDING = 4
    __CONTROL_BOTTOM_OFFSET = 20

    class Control:

        def __init__(self, icon_bitmap: Image, color: Tuple[int, int, int]):
            self._icon_bitmap = icon_bitmap
            self._color = color

        @property
        def size(self) -> Tuple[int, int]:
            return self._icon_bitmap.size

        def on_select(self):
            """When pressing button A"""
            pass

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            draw.bitmap(left_top, self._icon_bitmap, fill=self._color)

    class SwitchControl(Control):

        def __init__(self, icon_bitmap: Image, switched_icon_bitmap: Image, color: Tuple[int, int, int]):
            super().__init__(icon_bitmap, color)
            self._switched_icon_bitmap = switched_icon_bitmap
            self._color = color
            self._is_switched = False

        def on_select(self):
            self._is_switched = not self._is_switched

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            draw.bitmap(left_top, self._switched_icon_bitmap if self._is_switched else self._icon_bitmap,
                        fill=self._color)

    def __init__(self, resolution: Tuple[int, int],
                 background: Tuple[int, int, int], color: Tuple[int, int, int], color_dark: Tuple[int, int, int],
                 app_top_offset: int, app_side_offset: int, app_bottom_offset: int, font_standard: ImageFont):
        self.__resolution = resolution
        self.__background = background
        self.__color = color
        self.__color_dark = color_dark
        self.__app_top_offset = app_top_offset
        self.__app_side_offset = app_side_offset
        self.__app_bottom_offset = app_bottom_offset
        self.__font = font_standard

        self.__selected_index = 0
        self.__player = pyaudio.PyAudio()

        self.__supported_extensions = ['.wav']
        self.__files: Collection[str] = []

        resources_path = 'resources'
        stop_icon = Image.open(os.path.join(resources_path, 'stop.png')).convert('1')
        previous_icon = Image.open(os.path.join(resources_path, 'previous.png')).convert('1')
        play_icon = Image.open(os.path.join(resources_path, 'play.png')).convert('1')
        pause_icon = Image.open(os.path.join(resources_path, 'pause.png')).convert('1')
        skip_icon = Image.open(os.path.join(resources_path, 'skip.png')).convert('1')
        order_icon = Image.open(os.path.join(resources_path, 'order.png')).convert('1')
        random_icon = Image.open(os.path.join(resources_path, 'random.png')).convert('1')

        self.__controls = [
            self.Control(stop_icon, color),
            self.Control(previous_icon, color),
            self.SwitchControl(play_icon, pause_icon, color),
            self.Control(skip_icon, color),
            self.SwitchControl(order_icon, random_icon, color)
        ]
        self.__selected_control_index = 0

    @property
    def title(self) -> str:
        return 'RAD'

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        draw = ImageDraw.Draw(image)
        width, height = self.__resolution
        left_top = (self.__app_side_offset, self.__app_top_offset)

        # test draw controls
        controls_total_width = sum([c.size[0] for c in self.__controls]) + self.__CONTROL_PADDING * \
            (len(self.__controls) - 1)
        max_control_height = max([c.size[1] for c in self.__controls])
        cursor = (width // 2 - controls_total_width // 2,
                  height - self.__app_bottom_offset - max_control_height - self.__CONTROL_BOTTOM_OFFSET)
        for control in self.__controls:
            c_width, c_height = control.size
            control.draw(draw, (cursor[0], cursor[1] + (max_control_height - c_height) // 2))
            cursor = (cursor[0] + c_width + self.__CONTROL_PADDING, cursor[1])

        return image, 0, 0

    def __get_files(self):
        return sorted([f for f in os.listdir('media') if os.path.splitext(f)[1] in self.__supported_extensions],
                      key=str.lower)

    def on_key_left(self):
        self.__selected_control_index = max(self.__selected_control_index - 1, 0)

    def on_key_right(self):
        self.__selected_control_index = min(self.__selected_control_index + 1, len(self.__controls) - 1)

    def on_key_up(self):
        pass

    def on_key_down(self):
        pass

    def on_key_a(self):
        self.__controls[self.__selected_control_index].on_select()

    def on_key_b(self):
        pass

    def on_app_enter(self):
        self.__files = self.__get_files()

    def on_app_leave(self):
        pass
