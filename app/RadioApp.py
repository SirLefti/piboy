import os
import random
import re
from abc import ABC, abstractmethod
from subprocess import PIPE, run
from typing import Callable, Optional

from injector import inject
from PIL import Image, ImageDraw

from app.App import SelfUpdatingApp
from core import resources
from core.audio import MultiprocessingAudioPlayer
from core.decorator import override
from environment import AppConfig


class RadioApp(SelfUpdatingApp):
    __CONTROL_PADDING = 4
    __CONTROL_BOTTOM_OFFSET = 20
    __LINE_HEIGHT = 20
    __META_INFO_HEIGHT = 20
    __VOLUME_STEP = 10

    class ControlGroup:
        """
        Represents a group of control, where only a single control can be selected at the same time. Pass the control
        group instance as a parameter to the init block of a control, where it can call the `listen` function to be
        registered in this group. When selecting this control, it can call the `clear_selection` function to deselect
        every other control in the group.
        """

        def __init__(self):
            self.__controls: list['RadioApp.Control'] = []

        def listen(self, control: 'RadioApp.Control'):
            self.__controls.append(control)

        def clear_selection(self, control: Optional['RadioApp.Control']):
            for control in [c for c in self.__controls if c is not control]:
                control.reset()

    class Control(ABC):
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
            NONE: 'RadioApp.Control.SelectionState'
            FOCUSED: 'RadioApp.Control.SelectionState'

            def __init__(self, color: tuple[int, int, int], background_color: tuple[int, int, int],
                         is_focused: bool, is_selected: bool):
                self.__color = color
                self.__background_color = background_color
                self.__is_focused = is_focused
                self.__is_selected = is_selected

            @classmethod
            def from_state(cls, is_focused: bool, is_selected: bool) -> 'RadioApp.Control.SelectionState':
                values = [cls.NONE, cls.FOCUSED]
                return [state for state in values
                        if state.is_focused == is_focused and state.is_selected == is_selected][0]

            @property
            def is_focused(self) -> bool:
                return self.__is_focused

            @property
            def is_selected(self) -> bool:
                return self.__is_selected

            @property
            def color(self) -> tuple[int, int, int]:
                return self.__color

            @property
            def background_color(self) -> tuple[int, int, int]:
                return self.__background_color

        def __init__(self, icon_bitmap: Image.Image, control_group: Optional['RadioApp.ControlGroup'] = None):
            self._icon_bitmap = icon_bitmap
            self._selection_state = self.SelectionState.NONE
            self._control_group = control_group
            if self._control_group:
                self._control_group.listen(self)

        @property
        def size(self) -> tuple[int, int]:
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

        @abstractmethod
        def on_select(self):
            """When pressing the A button while focussing this control"""
            raise NotImplementedError

        def on_focus(self):
            """When moving focus on this control"""
            self._selection_state = self.SelectionState.FOCUSED

        def on_blur(self):
            """When moving focus away from this control"""
            self._selection_state = self.SelectionState.NONE

        def reset(self):
            """Resets the control to an unfocused state"""
            self._selection_state = self.SelectionState.NONE

        def draw(self, draw: ImageDraw.ImageDraw, left_top: tuple[int, int]):
            width, height = self._icon_bitmap.size
            left, top = left_top
            draw.rectangle(left_top + (left + width - 1, top + height - 1),
                           fill=self._selection_state.background_color)
            draw.bitmap(left_top, self._icon_bitmap, fill=self._selection_state.color)

    class SwitchControl(Control):
        """
        Represents a UI control element. A switch control has two textures, that can be switched on selection. Thus, it
        is never really in a selected state, but can switch between two states and can call different callbacks
        depending on this state.
        """

        def __init__(self, icon_bitmap: Image.Image, switched_icon_bitmap: Image.Image,
                     on_select: Callable[[], bool],
                     on_switched_select: Callable[[], bool],
                     control_group: Optional['RadioApp.ControlGroup'] = None):
            super().__init__(icon_bitmap, control_group)
            self._on_select = on_select
            self._on_switched_select = on_switched_select
            self._switched_icon_bitmap = switched_icon_bitmap
            self._is_switched = False

        def on_select(self):
            super()._handle_control_group()
            # this is inverted because we switch states after successful action
            if self._is_switched:
                if self._on_select():
                    self._is_switched = not self._is_switched
            else:
                if self._on_switched_select():
                    self._is_switched = not self._is_switched

        def on_deselect(self):
            self._is_switched = False

        def reset(self):
            self.on_blur()
            self.on_deselect()

        def draw(self, draw: ImageDraw.ImageDraw, left_top: tuple[int, int]):
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

        def __init__(self, icon_bitmap: Image.Image, on_select: Callable[[], None],
                     control_group: Optional['RadioApp.ControlGroup'] = None):
            super().__init__(icon_bitmap, control_group)
            self._on_select = on_select

        def on_select(self):
            super()._handle_control_group()
            self._on_select()

    __playback_control_group = ControlGroup()

    @inject
    def __init__(self, draw_callback: Callable[[bool], None], app_config: AppConfig):
        super().__init__(self.__self_update)
        self.__draw_callback = draw_callback
        self.__draw_callback_kwargs = {'partial': True}

        self.__resolution = app_config.resolution
        self.__background = app_config.background
        self.__color = app_config.accent
        self.__color_dark = app_config.accent_dark
        self.__app_top_offset = app_config.app_top_offset
        self.__app_side_offset = app_config.app_side_offset
        self.__app_bottom_offset = app_config.app_bottom_offset
        self.__font = app_config.font_standard

        self.__directory = 'media'
        self.__supported_extensions = ['.wav']
        self.__files: list[str] = self.__get_files()

        self.__selected_index = 0  # what we have selected with our cursor
        self.__top_index = 0  # what is on top in case the list is greater than screen space
        self.__playlist: list[int] = list(range(0, len(self.__files)))  # order of the tracks to play
        self.__playing_index = 0  # what we are currently playing from the playlist
        self.__is_random = False
        self.__volume: Optional[int] = None
        try:
            # will only work on raspberry pi for now
            self.__volume = self.__get_volume()
        except (FileNotFoundError, ValueError):
            pass

        self.__player = MultiprocessingAudioPlayer(self.__call_next)

        # init selection states
        self.Control.SelectionState.NONE = self.Control.SelectionState(self.__color_dark, self.__background, False, False)
        self.Control.SelectionState.FOCUSED = self.Control.SelectionState(self.__color, self.__background, True, False)

        control_group = self.ControlGroup()
        self.__controls = [
            self.InstantControl(resources.stop_icon, self.stop_action, control_group),
            self.InstantControl(resources.previous_icon, self.prev_action),
            self.SwitchControl(resources.play_icon, resources.pause_icon, self.pause_action, self.play_action, control_group),
            self.InstantControl(resources.skip_icon, self.skip_action),
            self.SwitchControl(resources.order_icon, resources.random_icon, self.order_action, self.random_action),
            self.InstantControl(resources.volume_decrease_icon, self.decrease_volume_action),
            self.InstantControl(resources.volume_increase_icon, self.increase_volume_action)
        ]
        self.__selected_control_index = 2

    def play_action(self) -> bool:
        """
        Loads current selected file if no stream is loaded.
        Resumes playing a loaded stream.
        :return: `True` if stream was started, else `False` (e.g. playlist is empty)
        """
        if len(self.__playlist) == 0:
            return False
        if self.__selected_index != self.__playlist[self.__playing_index]:
            self.__playing_index = self.__playlist.index(self.__selected_index)
            if self.__player.has_stream:
                self.__player.stop_stream()
        if not self.__player.has_stream:
            self.__player.load_file(os.path.join(self.__directory,
                                                 self.__files[self.__playlist[self.__playing_index]]))
        self.__player.start_stream()
        return True

    def pause_action(self) -> bool:
        """
        Pauses a currently loaded stream.
        :return: `True` if stream was paused, else `False` (e.g. there was no active stream)
        """
        return self.__player.pause_stream()

    def stop_action(self):
        """
        Stops and clears a currently loaded stream.
        """
        self.__player.stop_stream()

    def prev_action(self):
        """
        Stops and clears a stream, selects a previous track and plays it if a stream is loaded.
        Just selects a previous track otherwise.
        """
        self.__playing_index = (self.__playing_index - 1) % len(self.__files)
        self.__selected_index = self.__playlist[self.__playing_index]

        if self.__player.is_active:
            self.stop_action()
            self.play_action()

    def skip_action(self):
        """
        Stops and clears a stream, selects a next track and plays it if a stream is loaded.
        Just selects a next track otherwise.
        """
        self.__playing_index = (self.__playing_index + 1) % len(self.__files)
        self.__selected_index = self.__playlist[self.__playing_index]

        if self.__player.is_active:
            self.stop_action()
            self.play_action()

    def random_action(self) -> bool:
        """
        Shuffles the playlist and places the current index at the track we are currently playing or looking at.
        :return: always `True`
        """
        self.__is_random = True
        random.shuffle(self.__playlist)
        # set playlist index to the track we are currently playing or looking at
        self.__playing_index = self.__playlist.index(self.__selected_index)
        return True

    def order_action(self) -> bool:
        """
        Creates an ordered playlist and places the current index at the track we are currently playing or looking
        at.
        :return: always `True`
        """
        self.__is_random = False
        self.__playlist = list(range(0, len(self.__files)))
        # set playlist index to the track we are currently playing or looking at
        self.__playing_index = self.__selected_index
        return True

    def decrease_volume_action(self):
        """
        Decreases the volume by one volume step. Only works on Linux with `amixer`
        """
        current_value = self.__get_volume()
        if current_value % self.__VOLUME_STEP == 0:
            self.__set_volume(max(current_value - self.__VOLUME_STEP, 0))
        else:
            aligned_value = current_value // self.__VOLUME_STEP * self.__VOLUME_STEP
            self.__set_volume(max(aligned_value - self.__VOLUME_STEP, 0))
        self.__volume = self.__get_volume()

    def increase_volume_action(self):
        """
        Increases the volume by one volume step. Only works on Linux with `amixer`
        """
        current_value = self.__get_volume()
        if current_value % self.__VOLUME_STEP == 0:
            self.__set_volume(min(current_value + self.__VOLUME_STEP, 100))
        else:
            aligned_value = (current_value + self.__VOLUME_STEP) // self.__VOLUME_STEP * self.__VOLUME_STEP
            self.__set_volume(min(aligned_value + self.__VOLUME_STEP, 100))
        self.__volume = self.__get_volume()

    def __call_next(self):
        self.__playing_index = (self.__playing_index + 1) % len(self.__files)
        self.__selected_index = self.__playlist[self.__playing_index]
        self.__player.stop_stream()
        self.__player.load_file(os.path.join(self.__directory, self.__files[self.__playlist[self.__playing_index]]))
        self.__player.start_stream()

    def __self_update(self):
        self.__draw_callback(**self.__draw_callback_kwargs)

    @property
    @override
    def title(self) -> str:
        return 'RAD'

    @property
    @override
    def refresh_time(self) -> float:
        return 1.0

    @override
    def draw(self, image: Image.Image, partial=False) -> tuple[Image.Image, int, int]:
        draw = ImageDraw.Draw(image)
        width, height = self.__resolution

        # draw controls
        controls_total_width = sum([c.size[0] for c in self.__controls]) + self.__CONTROL_PADDING * (
                len(self.__controls) - 1)
        max_control_height = max([c.size[1] for c in self.__controls])
        cursor: tuple[int, int] = (width // 2 - controls_total_width // 2,
                                   height - self.__app_bottom_offset - max_control_height
                                   - self.__CONTROL_BOTTOM_OFFSET)
        for control in self.__controls:
            c_width, c_height = control.size
            control.draw(draw, (cursor[0], cursor[1] + (max_control_height - c_height) // 2))
            cursor = (cursor[0] + c_width + self.__CONTROL_PADDING, cursor[1])
        vertical_limit = cursor[1]

        # draw volume
        text = f'Volume: {self.__volume}%'
        _, _, t_width, t_height = self.__font.getbbox(text)
        draw.text((width // 2 - t_width // 2, vertical_limit - self.__META_INFO_HEIGHT // 2 - t_height // 2),
                  text, self.__color, font=self.__font)
        vertical_limit = vertical_limit - self.__META_INFO_HEIGHT

        # draw currently playing track
        max_width = width - 2 * self.__app_side_offset
        text = f'{self.__player.progress:.1%}: {self.__files[self.__playlist[self.__playing_index]]}' \
            if self.__player.has_stream else 'Empty'
        while self.__font.getbbox(text)[2] > max_width:
            text = text[:-1]  # cut off last char until it fits
        _, _, t_width, t_height = self.__font.getbbox(text)
        draw.text((width // 2 - t_width // 2, vertical_limit - self.__META_INFO_HEIGHT // 2 - t_height // 2),
                  text, self.__color, font=self.__font)
        vertical_limit = vertical_limit - self.__META_INFO_HEIGHT

        # draw track list
        left_top = (self.__app_side_offset, self.__app_top_offset)
        left, top = left_top
        right_bottom = (width - self.__app_side_offset, vertical_limit)
        right, bottom = right_bottom
        max_entries = (bottom - top) // self.__LINE_HEIGHT
        if len(self.__files) > max_entries:
            if self.__selected_index < self.__top_index:
                self.__top_index = self.__selected_index
            elif self.__selected_index not in range(self.__top_index, self.__top_index + max_entries):
                self.__top_index = self.__selected_index - max_entries + 1
        else:
            self.__top_index = 0
        cursor = left_top
        for index, file in enumerate(self.__files[self.__top_index:]):
            index += self.__top_index  # pad index if entries are skipped
            if self.__selected_index == index:
                draw.rectangle(cursor + (right, cursor[1] + self.__LINE_HEIGHT), self.__color_dark)
            if index == max_entries + self.__top_index:
                draw.text(cursor, '...', self.__color, font=self.__font)
                break
            text = file
            while self.__font.getbbox(text)[2] > right - left:
                text = text[:-1]  # cut off last char until it fits
            draw.text(cursor, text, self.__color, font=self.__font)
            cursor = (cursor[0], cursor[1] + self.__LINE_HEIGHT)

        if partial:
            right_bottom = width - self.__app_side_offset, height - self.__app_bottom_offset
            return image.crop(left_top + right_bottom), *left_top  # noqa (unpacking type check fail)
        else:
            return image, 0, 0

    def __get_files(self) -> list[str]:
        return sorted([f for f in os.listdir(self.__directory) if os.path.splitext(f)[1] in
                       self.__supported_extensions], key=lambda f: f.lower())

    @staticmethod
    def __get_volume() -> int:
        """
        Returns the current volume value on the primary sound mixer. Works only on Linux (Raspberry OS).
        :return: current volume value
        """
        # noinspection SpellCheckingInspection
        result = run(['amixer', '-M', 'sget', 'PCM'], stdout=PIPE)
        if result.returncode != 0:
            raise ValueError(f'Error getting current volume value: {result.returncode}')
        if result.stdout is not None:
            content = result.stdout.decode('utf-8')
            match = re.search(r'\[(\d+)%\]', content)  # noqa [Python Zen #2]: explicit is better than implicit
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
        if not 0 <= volume <= 100:
            raise ValueError(f'Error setting volume value: Volume must be between 0 and 100, was {volume}')
        # noinspection SpellCheckingInspection
        result = run(['amixer', '-q', '-M', 'sset', 'PCM', f'{volume}%'], stdout=PIPE)
        if result.returncode != 0:
            raise ValueError(f'Error setting volume value: {result.returncode}')

    @override
    def on_key_left(self):
        self.__controls[self.__selected_control_index].on_blur()
        self.__selected_control_index = max(self.__selected_control_index - 1, 0)
        self.__controls[self.__selected_control_index].on_focus()

    @override
    def on_key_right(self):
        self.__controls[self.__selected_control_index].on_blur()
        self.__selected_control_index = min(self.__selected_control_index + 1, len(self.__controls) - 1)
        self.__controls[self.__selected_control_index].on_focus()

    @override
    def on_key_up(self):
        self.__selected_index = max(self.__selected_index - 1, 0)

    @override
    def on_key_down(self):
        self.__selected_index = min(self.__selected_index + 1, len(self.__files) - 1)

    @override
    def on_key_a(self):
        self.__controls[self.__selected_control_index].on_select()

    @override
    def on_app_enter(self):
        super().on_app_enter()
        self.__controls[self.__selected_control_index].on_focus()
