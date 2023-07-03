from app.App import App
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List, Callable, Optional
from subprocess import run, PIPE
import pyaudio
import wave
import os
import re


class RadioApp(App):
    __CONTROL_PADDING = 4
    __CONTROL_BOTTOM_OFFSET = 20
    __MAX_ENTRIES = 9
    __LINE_HEIGHT = 20
    __VOLUME_STEP = 10

    class ControlGroup:
        """
        Represents a group of control, where only a single control can be selected at the same time. Pass the control
        group instance as a parameter to the init block of a control, where it can call the `listen` function to be
        registered in this group. When selecting this control, it can call the `clear_selection` function to deselect
        every other control in the group.
        """

        def __init__(self):
            self.__controls: List['RadioApp.Control'] = []

        def listen(self, control: 'RadioApp.Control'):
            self.__controls.append(control)

        def clear_selection(self, control: 'RadioApp.Control'):
            for control in [c for c in self.__controls if c is not control]:
                control.on_deselect()

    class Control:
        """
        Represents a UI control element. A control has a texture, a callback and might have a control group that
        unselects other controls in the same group, if this control gets selected.
        """

        class SelectionState:
            """
            Container class representing a state of a control element. A selection state has an element color and
            a background color, and also values determining if it represents focused and selected.
            Initially, the state members are all none, replace them before usage or create new ones for a specific use.
            """
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

        def __init__(self, icon_bitmap: Image, on_select: Callable[[], None],
                     control_group: 'RadioApp.ControlGroup' = None):
            self._icon_bitmap = icon_bitmap
            self._selection_state = self.SelectionState.NONE
            self._on_select = on_select
            self._control_group = control_group
            if self._control_group:
                self._control_group.listen(self)

        @property
        def size(self) -> Tuple[int, int]:
            return self._icon_bitmap.size

        @property
        def is_focused(self) -> bool:
            return self._selection_state.is_focused

        @property
        def is_selected(self) -> bool:
            return self._selection_state.is_selected

        def _handle_control_group(self):
            """Clears selection in the same control group"""
            if not self.is_selected:
                if self._control_group:
                    self._control_group.clear_selection(self)

        def on_select(self):
            """When pressing button A"""
            self._handle_control_group()
            self._selection_state = self.SelectionState.from_state(self.is_focused, True)
            self._on_select()

        def on_deselect(self):
            """When pressing button B or selecting a different control in the same group"""
            self._selection_state = self.SelectionState.from_state(self.is_focused, False)

        def on_focus(self):
            """When moving focus on this control"""
            self._selection_state = self.SelectionState.from_state(True, self.is_selected)

        def on_blur(self):
            """When moving focus away from this control"""
            self._selection_state = self.SelectionState.from_state(False, self.is_selected)

        def reset(self):
            """Resets the control to and unfocused and unselected state"""
            self._selection_state = self.SelectionState.from_state(False, False)

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            width, height = self._icon_bitmap.size
            left, top = left_top
            draw.rectangle(left_top + (left + width - 1, top + height - 1),
                           fill=self._selection_state.background_color)
            draw.bitmap(left_top, self._icon_bitmap, fill=self._selection_state.color)

    class SingleActionControl(Control):
        """
        Represents a UI control element. A single action control is a simple type of control. If it is already selected,
        it cannot be selected again and has to be deselected in some way (either by a key or by a control group).
        """

        def __init__(self, icon_bitmap: Image, on_select: Callable[[], None],
                     control_group: 'RadioApp.ControlGroup' = None):
            super().__init__(icon_bitmap, on_select, control_group)

        def on_select(self):
            if not self.is_selected:
                super()._handle_control_group()
                self._selection_state = self.SelectionState.from_state(self.is_focused, True)
                self._on_select()

    class SwitchControl(Control):
        """
        Represents a UI control element. A switch control has two textures, that can be switched on selection. Thus, it
        is never really in a selected state, but can switch between two states and can call different callbacks
        depending on this state.
        """

        def __init__(self, icon_bitmap: Image, switched_icon_bitmap: Image,
                     on_select: Callable[[], None],
                     on_switched_select: Callable[[], None],
                     control_group: 'RadioApp.ControlGroup' = None):
            super().__init__(icon_bitmap, on_select, control_group)
            self._on_switched_select = on_switched_select
            self._switched_icon_bitmap = switched_icon_bitmap
            self._is_switched = False

        def on_select(self):
            super()._handle_control_group()
            self._is_switched = not self._is_switched
            if self._is_switched:
                self._on_switched_select()
            else:
                self._on_select()

        def on_deselect(self):
            self._is_switched = False

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            width, height = self._icon_bitmap.size
            left, top = left_top
            draw.rectangle(left_top + (left + width - 1, top + height - 1),
                           fill=self._selection_state.background_color)
            draw.bitmap(left_top, self._switched_icon_bitmap if self._is_switched else self._icon_bitmap,
                        fill=self._selection_state.color)

    class InstantControl(Control):
        """
        Represents a UI control element. An instant control can never be selected. When selecting, it only calls the
        callback but stays in the same state, allowing to call the action again.
        """

        def __init__(self, icon_bitmap: Image, on_select: Callable[[], None],
                     control_group: 'RadioApp.ControlGroup' = None):
            super().__init__(icon_bitmap, on_select, control_group)

        def on_select(self):
            super()._handle_control_group()
            self._on_select()

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
        self.__top_index = 0
        self.__player = pyaudio.PyAudio()
        self.__stream: Optional[pyaudio.Stream] = None
        self.__wave = None
        self.__is_playing = False
        self.__is_random = False

        self.__directory = 'media'
        self.__supported_extensions = ['.wav']
        self.__files: List[str] = []

        # init selection states
        self.Control.SelectionState.NONE = self.Control.SelectionState(color_dark, background, False, False)
        self.Control.SelectionState.FOCUSED = self.Control.SelectionState(color, background, True, False)
        self.Control.SelectionState.SELECTED = self.Control.SelectionState(color_dark, color, False, True)
        self.Control.SelectionState.FOCUSED_SELECTED = self.Control.SelectionState(color, color_dark, True, True)

        resources_path = 'resources'
        stop_icon = Image.open(os.path.join(resources_path, 'stop.png')).convert('1')
        previous_icon = Image.open(os.path.join(resources_path, 'previous.png')).convert('1')
        play_icon = Image.open(os.path.join(resources_path, 'play.png')).convert('1')
        pause_icon = Image.open(os.path.join(resources_path, 'pause.png')).convert('1')
        skip_icon = Image.open(os.path.join(resources_path, 'skip.png')).convert('1')
        order_icon = Image.open(os.path.join(resources_path, 'order.png')).convert('1')
        random_icon = Image.open(os.path.join(resources_path, 'random.png')).convert('1')
        volume_decrease_icon = Image.open(os.path.join(resources_path, 'volume_decrease.png')).convert('1')
        volume_increase_icon = Image.open(os.path.join(resources_path, 'volume_increase.png')).convert('1')

        def stream_callback(_1, frame_count, _2,  _3):
            data = self.__wave.readframes(frame_count)
            return data, pyaudio.paContinue

        def play_action():
            """
            Loads current selected file if no stream is loaded.
            Resumes playing a loaded stream.
            """
            if not self.__stream:
                self.__wave = wave.open(os.path.join(self.__directory, self.__files[self.__selected_index]), 'rb')
                self.__stream = self.__player.open(format=self.__player.get_format_from_width(
                                                          self.__wave.getsampwidth()),
                                                   channels=self.__wave.getnchannels(),
                                                   rate=self.__wave.getframerate(),
                                                   output=True,
                                                   stream_callback=stream_callback)
            self.__stream.start_stream()
            self.__is_playing = True

        def pause_action():
            """Pauses a currently loaded stream."""
            if self.__stream:
                self.__stream.stop_stream()
                self.__is_playing = False

        def stop_action():
            """Stops and clears a currently loaded stream."""
            if self.__stream:
                self.__stream.stop_stream()
                self.__stream.close()
                self.__is_playing = False
                self.__stream = None

        def prev_action():
            """
            Stops and clears a stream, selects a previous track and plays it if a stream is loaded.
            Just selects a previous track otherwise.
            """
            if self.__stream and self.__is_playing:
                self.__stream.stop_stream()
                self.__stream.close()
                self.__stream = None
                if self.__is_random:
                    # TODO implement randomization
                    pass
                else:
                    self.__selected_index = max(self.__selected_index - 1, 0)
                play_action()
            else:
                if self.__is_random:
                    # TODO implement randomization
                    pass
                else:
                    self.__selected_index = max(self.__selected_index - 1, 0)

        def skip_action():
            """
            Stops and clears a stream, selects a next track and plays it if a stream is loaded.
            Just selects a next track otherwise.
            """
            if self.__stream and self.__is_playing:
                self.__stream.stop_stream()
                self.__stream.close()
                self.__stream = None
                if self.__is_random:
                    # TODO implement randomization
                    pass
                else:
                    self.__selected_index = min(self.__selected_index + 1, len(self.__files) - 1)
                play_action()
            else:
                if self.__is_random:
                    # TODO implement randomization
                    pass
                else:
                    self.__selected_index = min(self.__selected_index + 1, len(self.__files) - 1)

        def random_action():
            self.__is_random = True

        def order_action():
            self.__is_random = False

        def decrease_volume_action():
            current_value = self.__get_volume()
            if current_value % self.__VOLUME_STEP == 0:
                self.__set_volume(max(current_value - self.__VOLUME_STEP, 0))
            else:
                aligned_value = current_value // self.__VOLUME_STEP * self.__VOLUME_STEP
                self.__set_volume(max(aligned_value - self.__VOLUME_STEP, 0))

        def increase_volume_action():
            current_value = self.__get_volume()
            if current_value % self.__VOLUME_STEP == 0:
                self.__set_volume(min(current_value + self.__VOLUME_STEP, 100))
            else:
                aligned_value = (current_value + self.__VOLUME_STEP) // self.__VOLUME_STEP * self.__VOLUME_STEP
                self.__set_volume(min(aligned_value + self.__VOLUME_STEP, 100))

        control_group = self.ControlGroup()
        self.__controls = [
            self.InstantControl(stop_icon, stop_action, control_group),
            self.InstantControl(previous_icon, prev_action, control_group),
            self.SwitchControl(play_icon, pause_icon, pause_action, play_action, control_group),
            self.InstantControl(skip_icon, skip_action, control_group),
            self.SwitchControl(order_icon, random_icon, order_action, random_action),
            self.InstantControl(volume_decrease_icon, decrease_volume_action),
            self.InstantControl(volume_increase_icon, increase_volume_action)
        ]
        self.__selected_control_index = 2

    @property
    def title(self) -> str:
        return 'RAD'

    def draw(self, image: Image, partial=False) -> (Image, int, int):
        draw = ImageDraw.Draw(image)
        width, height = self.__resolution

        # draw controls
        controls_total_width = sum([c.size[0] for c in self.__controls]) + self.__CONTROL_PADDING * (
                len(self.__controls) - 1)
        max_control_height = max([c.size[1] for c in self.__controls])
        cursor = (width // 2 - controls_total_width // 2,
                  height - self.__app_bottom_offset - max_control_height - self.__CONTROL_BOTTOM_OFFSET)
        for control in self.__controls:
            c_width, c_height = control.size
            control.draw(draw, (cursor[0], cursor[1] + (max_control_height - c_height) // 2))
            cursor = (cursor[0] + c_width + self.__CONTROL_PADDING, cursor[1])

        # draw track list
        left_top = (self.__app_side_offset, self.__app_top_offset)
        left, top = left_top
        right_bottom = (width - self.__app_side_offset, top + self.__LINE_HEIGHT * self.__MAX_ENTRIES)
        right, bottom = right_bottom

        if len(self.__files) > self.__MAX_ENTRIES:
            if self.__selected_index < self.__top_index:
                self.__top_index = self.__selected_index
            elif self.__selected_index not in range(self.__top_index, self.__top_index + self.__MAX_ENTRIES):
                self.__top_index = self.__selected_index - self.__MAX_ENTRIES + 1
        else:
            self.__top_index = 0

        cursor = left_top
        for index, file in enumerate(self.__files[self.__top_index:]):
            index += self.__top_index  # pad index if entries are skipped
            if self.__selected_index == index:
                draw.rectangle(cursor + (right, cursor[1] + self.__LINE_HEIGHT), self.__color_dark)

            if index == self.__MAX_ENTRIES + self.__top_index:
                draw.text(cursor, '...', self.__color, font=self.__font)
                break

            text = file
            while self.__font.getbbox(text)[2] > right - left:
                text = text[:-1]  # cut off last char until it fits

            draw.text(cursor, text, self.__color, font=self.__font)
            cursor = (cursor[0], cursor[1] + self.__LINE_HEIGHT)

        return image, 0, 0

    def __get_files(self):
        return sorted([f for f in os.listdir(self.__directory) if os.path.splitext(f)[1] in
                       self.__supported_extensions], key=str.lower)

    @staticmethod
    def __get_volume() -> int:
        """
        Returns the current volume value on the primary sound mixer. Works only on Linux (Raspberry OS).
        :return: current volume value
        """
        result = run(['amixer', '-M', 'sget', 'PCM'], stdout=PIPE)
        if result.returncode != 0:
            raise ValueError(f'Error getting current volume value: {result.returncode}')
        if result.stdout is not None:
            content = result.stdout.decode('utf-8')
            # (Python Zen #2) explicit is better than implicit, the second backslash should stay there
            match = re.search(r'\[(\d+)%\]', content)
            if match:
                return int(match.group(1))
            else:
                raise ValueError('Error getting current volume: No match')
        raise ValueError('Error getting current volume value: No content')

    @staticmethod
    def __set_volume(volume: int):
        """
        Updates the volume value on the primary sound mixer. Value must be between 0 and 100 (inclusive).
        Works only on Linux (Raspberry OS).
        :param volume: volume value to set
        """
        # python allows this mathematical expression unlike other languages
        if 0 <= volume <= 100:
            raise ValueError('Error setting volume value: Volume must be between 0 and 100')
        result = run(['amixer', '-q', '-M', 'sset', 'PCM', f'{volume}%'], stdout=PIPE)
        if result.returncode != 0:
            raise ValueError(f'Error setting volume value: {result.returncode}')

    def on_key_left(self):
        self.__controls[self.__selected_control_index].on_blur()
        self.__selected_control_index = max(self.__selected_control_index - 1, 0)
        self.__controls[self.__selected_control_index].on_focus()

    def on_key_right(self):
        self.__controls[self.__selected_control_index].on_blur()
        self.__selected_control_index = min(self.__selected_control_index + 1, len(self.__controls) - 1)
        self.__controls[self.__selected_control_index].on_focus()

    def on_key_up(self):
        self.__selected_index = max(self.__selected_index - 1, 0)

    def on_key_down(self):
        self.__selected_index = min(self.__selected_index + 1, len(self.__files) - 1)

    def on_key_a(self):
        self.__controls[self.__selected_control_index].on_select()

    def on_key_b(self):
        pass

    def on_app_enter(self):
        self.__files = self.__get_files()
        self.__controls[self.__selected_control_index].on_focus()

    def on_app_leave(self):
        pass
