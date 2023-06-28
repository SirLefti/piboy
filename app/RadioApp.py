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

        class SelectionState:
            NONE = None
            FOCUSED = None
            SELECTED = None
            FOCUSED_SELECTED = None

            def __init__(self, color: Tuple[int, int, int], background_color: Tuple[int, int, int],
                         is_focused: bool, is_selected: bool):
                self.__color = color
                self.__background_color = background_color
                self.__is_focused = is_focused
                self.__is_selected = is_selected

            @classmethod
            def from_state(cls, is_focused: bool, is_selected: bool):
                values = [cls.NONE, cls.FOCUSED, cls.SELECTED, cls.FOCUSED_SELECTED]
                return [state for state in values
                        if state.is_focused == is_focused and state.is_selected == is_selected][0]

            @property
            def is_focused(self):
                return self.__is_focused

            @property
            def is_selected(self):
                return self.__is_selected

            @property
            def color(self) -> Tuple[int, int, int]:
                return self.__color

            @property
            def background_color(self):
                return self.__background_color

        def __init__(self, icon_bitmap: Image):
            self._icon_bitmap = icon_bitmap
            self._selection_state = self.SelectionState.NONE

        @property
        def size(self) -> Tuple[int, int]:
            return self._icon_bitmap.size

        @property
        def is_focused(self) -> bool:
            return self._selection_state.is_focused

        @property
        def is_selected(self) -> bool:
            return self._selection_state.is_selected

        def on_select(self):
            """When pressing button A"""
            self._selection_state = self.SelectionState.from_state(self.is_focused, True)

        def on_deselect(self):
            """When pressing button B or selecting a different control"""
            self._selection_state = self.SelectionState.from_state(self.is_focused, False)

        def on_focus(self):
            """When moving focus on this control"""
            self._selection_state = self.SelectionState.from_state(True, self.is_selected)

        def on_blur(self):
            """When moving focus away from this control"""
            self._selection_state = self.SelectionState.from_state(False, self.is_selected)

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            width, height = self._icon_bitmap.size
            left, top = left_top
            draw.rectangle(left_top + (left + width - 1, top + height - 1),
                           fill=self._selection_state.background_color)
            draw.bitmap(left_top, self._icon_bitmap, fill=self._selection_state.color)

    class SwitchControl(Control):

        def __init__(self, icon_bitmap: Image, switched_icon_bitmap: Image):
            super().__init__(icon_bitmap)
            self._switched_icon_bitmap = switched_icon_bitmap
            self._is_switched = False

        def on_select(self):
            self._is_switched = not self._is_switched

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            width, height = self._icon_bitmap.size
            left, top = left_top
            draw.rectangle(left_top + (left + width - 1, top + height - 1),
                           fill=self._selection_state.background_color)
            draw.bitmap(left_top, self._switched_icon_bitmap if self._is_switched else self._icon_bitmap,
                        fill=self._selection_state.color)

    class InstantControl(Control):

        def __init__(self, icon_bitmap: Image):
            super().__init__(icon_bitmap)

        def on_select(self):
            pass

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

        # init selection states
        self.Control.SelectionState.NONE = self.Control.SelectionState(color_dark, background, False, False)
        self.Control.SelectionState.FOCUSED = self.Control.SelectionState(color, background, True, False)
        self.Control.SelectionState.SELECTED = self.Control.SelectionState(background, color_dark, False, True)
        self.Control.SelectionState.FOCUSED_SELECTED = self.Control.SelectionState(background, color, True, True)

        resources_path = 'resources'
        stop_icon = Image.open(os.path.join(resources_path, 'stop.png')).convert('1')
        previous_icon = Image.open(os.path.join(resources_path, 'previous.png')).convert('1')
        play_icon = Image.open(os.path.join(resources_path, 'play.png')).convert('1')
        pause_icon = Image.open(os.path.join(resources_path, 'pause.png')).convert('1')
        skip_icon = Image.open(os.path.join(resources_path, 'skip.png')).convert('1')
        order_icon = Image.open(os.path.join(resources_path, 'order.png')).convert('1')
        random_icon = Image.open(os.path.join(resources_path, 'random.png')).convert('1')

        self.__controls = [
            self.Control(stop_icon),
            self.InstantControl(previous_icon),
            self.SwitchControl(play_icon, pause_icon),
            self.InstantControl(skip_icon),
            self.SwitchControl(order_icon, random_icon)
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
        self.__controls[self.__selected_control_index].on_blur()
        self.__selected_control_index = max(self.__selected_control_index - 1, 0)
        self.__controls[self.__selected_control_index].on_focus()

    def on_key_right(self):
        self.__controls[self.__selected_control_index].on_blur()
        self.__selected_control_index = min(self.__selected_control_index + 1, len(self.__controls) - 1)
        self.__controls[self.__selected_control_index].on_focus()

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
        self.__controls[self.__selected_control_index].on_focus()

    def on_app_leave(self):
        pass
