import os
import shutil
from typing import Callable, Optional

from injector import inject
from PIL import Image, ImageDraw, ImageOps

from app.App import App
from core import resources
from core.decorator import override
from environment import AppConfig


class FileManagerApp(App):
    POPUP_BORDER = 3
    LINE_HEIGHT = 20

    class DirectoryState:

        class ErrorMessage:

            def __init__(self, message: str):
                self.__message = message

            @property
            def message(self) -> str:
                return self.__message

        class Popup:

            def __init__(self, options: list[str], actions: list[Callable]):
                if len(options) != len(actions):
                    raise ValueError(
                        'There must be as many options as actions ({0}, {1})'.format(len(options), len(actions)))
                self.__options = options
                self.__selected_index = 0
                self.__actions = actions

            @property
            def options(self) -> list[str]:
                return self.__options

            @property
            def selected_index(self) -> int:
                return self.__selected_index

            def increase_index(self):
                self.__selected_index = min(self.__selected_index + 1, len(self.__options) - 1)

            def decrease_index(self):
                self.__selected_index = max(self.__selected_index - 1, 0)

            def action(self):
                self.__actions[self.__selected_index]()

        def __init__(self):
            self.__directory = os.path.expanduser('~')
            self.__top_index = 0
            self.__selected_index = 0
            self.__popup = None
            self.__error_message = None

        @property
        def directory(self) -> str:
            return self.__directory

        @directory.setter
        def directory(self, value: str):
            self.__directory = value

        @property
        def top_index(self) -> int:
            return self.__top_index

        @top_index.setter
        def top_index(self, value: int):
            self.__top_index = value

        @property
        def selected_index(self) -> int:
            return self.__selected_index

        @selected_index.setter
        def selected_index(self, value: int):
            self.__selected_index = value

        def increase_index(self):
            self.__selected_index = min(self.__selected_index + 1, self.entries - 1)

        def decrease_index(self):
            self.__selected_index = max(self.__selected_index - 1, 0)

        @property
        def popup(self) -> Optional[Popup]:
            return self.__popup

        @popup.setter
        def popup(self, value: Popup):
            self.__popup = value

        def remove_popup(self):
            self.__popup = None

        @property
        def error_message(self) -> Optional[ErrorMessage]:
            return self.__error_message

        @error_message.setter
        def error_message(self, value: ErrorMessage):
            self.__error_message = value

        def remove_error_message(self):
            self.__error_message = None

        @property
        def entries(self) -> int:
            return len(self.files)

        @property
        def files(self) -> list[str]:
            return sorted([f for f in os.listdir(self.__directory)], key=lambda f: f.lower())

    @inject
    def __init__(self, app_config: AppConfig):
        self.__resolution = app_config.resolution
        self.__background = app_config.background
        self.__color = app_config.accent
        self.__color_dark = app_config.accent_dark
        self.__app_top_offset = app_config.app_top_offset
        self.__app_side_offset = app_config.app_side_offset
        self.__app_bottom_offset = app_config.app_bottom_offset
        self.__font = app_config.font_standard

        self.__left_directory = self.DirectoryState()
        self.__right_directory = self.DirectoryState()
        self.__selected_tab = 0  # 0 for left, 1 for right
        self.__tab_changed = False
        pass

    def __change_tab(self):
        self.__selected_tab ^= 1
        self.__tab_changed = True

    @property
    def __active_directory(self) -> DirectoryState:
        if self.__selected_tab:
            return self.__right_directory
        else:
            return self.__left_directory

    @property
    def __other_directory(self) -> DirectoryState:
        if self.__selected_tab:
            return self.__left_directory
        else:
            return self.__right_directory

    @property
    @override
    def title(self) -> str:
        return "INV"

    @classmethod
    def __next_even(cls, value: int):
        """Returns the next even number, if the number is not even."""
        if value % 2:
            return value + 1
        else:
            return value

    def __draw_popup(self, draw: ImageDraw.ImageDraw, left_top: tuple[int, int], right_bottom: tuple[int, int],
                     popup: DirectoryState.Popup):
        """Draws a popup with the given options."""
        line_height = self.LINE_HEIGHT
        popup_border = self.POPUP_BORDER
        popup_min_width = 150
        font = self.__font
        left, top = left_top
        right, bottom = right_bottom

        options_widths = [int(font.getbbox(text)[2]) for text in popup.options]
        popup_width = self.__next_even(
            max(max(options_widths), popup_min_width)
        )  # require at least popup_min_width
        popup_height = line_height * len(popup.options)

        center = left + int((right - left) / 2), top + int((bottom - top) / 2)

        start = center[0] - int(popup_width / 2) - popup_border, center[1] - int(popup_height / 2) - popup_border
        end = center[0] + int(popup_width / 2) + popup_border, center[1] + int(popup_height / 2) + popup_border
        draw.rectangle(start + end, fill=self.__color)
        start = center[0] - int(popup_width / 2), center[1] - int(popup_height / 2)
        end = center[0] + int(popup_width / 2), center[1] + int(popup_height / 2)
        draw.rectangle(start + end, fill=self.__background)

        cursor = start
        for index, text in enumerate(popup.options):
            if index == popup.selected_index:
                draw.rectangle((cursor, (cursor[0] + popup_width, cursor[1] + line_height)), fill=self.__color_dark)
            draw.text(cursor, text, self.__color, font=font)
            cursor = cursor[0], cursor[1] + line_height

    def __draw_error(self, draw: ImageDraw.ImageDraw, left_top: tuple[int, int], right_bottom: tuple[int, int],
                     text: str):
        left, top = left_top  # unpacking top left anchor point
        right, bottom = right_bottom  # unpacking bottom right anchor point
        font = self.__font
        _, _, text_width, text_height = font.getbbox(text)
        popup_width = text_width + 10
        popup_height = text_height * 3
        popup_border = self.POPUP_BORDER
        center = left + int((right - left) / 2), top + int((bottom - top) / 2)

        start = center[0] - int(popup_width / 2) - popup_border, center[1] - int(popup_height / 2) - popup_border
        end = center[0] + int(popup_width / 2) + popup_border, center[1] + int(popup_height / 2) + popup_border
        draw.rectangle(start + end, fill=self.__color)
        start = start[0] + popup_border, start[1] + popup_border
        end = end[0] - popup_border, end[1] - popup_border
        draw.rectangle(start + end, fill=self.__background)
        draw.text((center[0] - int(text_width / 2), center[1] - int(text_height / 2)), text, self.__color, font=font)

    def __draw_directory(self, draw: ImageDraw.ImageDraw, left_top: tuple[int, int], right_bottom: tuple[int, int],
                         state: DirectoryState, is_selected: bool) -> None:
        """Draws the given directory to the given ImageDraw and returns the new top_index."""
        line_height = self.LINE_HEIGHT  # height of a line entry in the directory
        side_padding = 3  # padding to the side of the directory background
        symbol_dimensions = 10  # size of symbol entry
        symbol_padding = (line_height - symbol_dimensions) // 2  # space around symbol
        left, top = left_top  # unpacking top left anchor point
        right, bottom = right_bottom  # unpacking bottom right anchor point
        font = self.__font

        # draw background if this directory is selected
        if is_selected:
            draw.rectangle(left_top + right_bottom, fill=self.__color_dark)
        text = state.directory
        while font.getbbox(text)[2] > right - left - side_padding:
            text = text[:-1]  # cut off last char until it fits
        draw.text((left + side_padding, top), text, self.__color, font=font)

        cursor = (left, top + line_height)
        try:
            content = state.files
            entries = state.entries
            max_entries = (bottom - cursor[1]) // line_height
            max_entries -= 1 if entries > max_entries else 0  # reduce max shown entries to show the ... line if needed
            if entries > max_entries:  # not all entries will fit in the view
                if state.selected_index < state.top_index:
                    state.top_index = state.selected_index
                elif state.selected_index not in range(state.top_index, state.top_index + max_entries):
                    state.top_index = state.selected_index - max_entries + 1
            else:  # all entries will fit, set top_index to 0
                state.top_index = 0

            for index, file in enumerate(content[state.top_index:]):
                cursor_x, cursor_y = cursor
                index += state.top_index  # pad index if entries are skipped
                if state.selected_index == index and is_selected:
                    draw.rectangle((left, cursor_y, right, cursor_y + line_height), fill=self.__background)

                start = (left + symbol_padding, cursor_y + symbol_padding)
                end = (left + symbol_padding + symbol_dimensions, cursor_y + symbol_padding + symbol_dimensions)
                if end[1] > bottom - line_height:
                    draw.text((cursor_x + side_padding, cursor_y), '...', self.__color, font=font)
                    break

                if os.path.isfile(os.path.join(state.directory, file)):
                    draw.bitmap(start, ImageOps.invert(resources.file_icon), fill=self.__color)
                else:
                    draw.bitmap(start, ImageOps.invert(resources.directory_icon), fill=self.__color)

                while font.getbbox(file)[2] > right - left - symbol_dimensions - 2 * symbol_padding:
                    file = file[:-1]  # cut off last char until it fits
                draw.text((cursor_x + symbol_dimensions + 2 * symbol_padding, cursor_y), file, self.__color, font=font)
                cursor = (cursor_x, cursor_y + line_height)

            if state.error_message is not None:
                self.__draw_error(draw, left_top, right_bottom, state.error_message.message)
            elif state.popup is not None:
                self.__draw_popup(draw, left_top, right_bottom, state.popup)

        except PermissionError:
            self.__draw_error(draw, left_top, right_bottom, 'Permission denied')

    @override
    def draw(self, image: Image.Image, partial=False) -> tuple[Image.Image, int, int]:
        width, height = self.__resolution
        is_left_tab = self.__selected_tab == 0
        is_right_tab = self.__selected_tab == 1
        tab_changed = self.__tab_changed
        self.__tab_changed = False  # resetting but keep value
        draw_left = not partial or is_left_tab or tab_changed
        draw_right = not partial or is_right_tab or tab_changed
        draw = ImageDraw.Draw(image)

        if draw_left:
            left_top = (self.__app_side_offset, self.__app_top_offset)
            right_bottom = (int(width / 2) - 1, height - self.__app_bottom_offset)
            self.__draw_directory(draw, left_top, right_bottom, self.__left_directory, is_selected=is_left_tab)
            if partial and not tab_changed:
                return image.crop(left_top + right_bottom), *left_top  # noqa (unpacking type check fail)

        if draw_right:
            left_top = (int(width / 2) + 1, self.__app_top_offset)
            right_bottom = (width - self.__app_side_offset, height - self.__app_bottom_offset)
            self.__draw_directory(draw, left_top, right_bottom, self.__right_directory, is_selected=is_right_tab)
            if partial and not tab_changed:
                return image.crop(left_top + right_bottom), *left_top   # noqa (unpacking type check fail)

        # split line
        start = (width / 2 - 1, self.__app_top_offset)
        end = (width / 2, height - self.__app_bottom_offset)
        draw.rectangle(start + end, fill=self.__color)

        if partial:
            left_top = (self.__app_side_offset, self.__app_top_offset)
            right_bottom = (width - self.__app_side_offset, height - self.__app_bottom_offset)
            return image.crop(left_top + right_bottom), *left_top   # noqa (unpacking type check fail)
        else:
            return image, 0, 0

    def _enter(self):
        path = os.path.join(self.__active_directory.directory, self.__active_directory.files[self.__active_directory
                            .selected_index])
        self.__active_directory.directory = path
        self.__active_directory.selected_index = 0
        self.__active_directory.remove_popup()

    def _copy(self):
        source_path = os.path.join(self.__active_directory.directory, self.__active_directory.files[
            self.__active_directory.selected_index])
        target_path = os.path.join(self.__other_directory.directory, self.__active_directory.files[
            self.__active_directory.selected_index])
        if source_path != target_path:
            try:
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, target_path, dirs_exist_ok=True)
                else:
                    shutil.copy(source_path, target_path)
            except PermissionError:
                self.__active_directory.error_message = self.DirectoryState.ErrorMessage('Permission denied')
            except FileExistsError:
                self.__active_directory.error_message = self.DirectoryState.ErrorMessage('File already exists')
        self.__active_directory.remove_popup()

    def _move(self):
        source_path = os.path.join(self.__active_directory.directory, self.__active_directory.files[
            self.__active_directory.selected_index])
        target_path = os.path.join(self.__other_directory.directory, self.__active_directory.files[
            self.__active_directory.selected_index])
        if source_path != target_path:
            try:
                shutil.move(source_path, target_path)
            except PermissionError:
                self.__active_directory.error_message = self.DirectoryState.ErrorMessage('Permission denied')
            except FileExistsError:
                self.__active_directory.error_message = self.DirectoryState.ErrorMessage('File already exists')
        self.__active_directory.remove_popup()

    def _delete(self):
        path = os.path.join(self.__active_directory.directory, self.__active_directory.files[self.__active_directory
                            .selected_index])
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except PermissionError:
            self.__active_directory.error_message = self.DirectoryState.ErrorMessage('Permission denied')
        self.__active_directory.remove_popup()

    @override
    def on_key_left(self):
        if self.__active_directory.popup is None and self.__active_directory.error_message is None:
            self.__change_tab()

    @override
    def on_key_right(self):
        if self.__active_directory.popup is None and self.__active_directory.error_message is None:
            self.__change_tab()

    @override
    def on_key_up(self):
        if self.__active_directory.error_message is not None:
            pass
        elif self.__active_directory.popup is not None:
            self.__active_directory.popup.decrease_index()
        else:
            self.__active_directory.decrease_index()

    @override
    def on_key_down(self):
        if self.__active_directory.error_message is not None:
            pass
        elif self.__active_directory.popup is not None:
            self.__active_directory.popup.increase_index()
        else:
            self.__active_directory.increase_index()

    @override
    def on_key_a(self):
        path = os.path.join(self.__active_directory.directory, self.__active_directory.files[self.__active_directory
                            .selected_index])
        if self.__active_directory.error_message is not None:
            pass
        elif self.__active_directory.popup is not None:
            self.__active_directory.popup.action()
        else:
            if os.path.isdir(path):
                self.__active_directory.popup = self.DirectoryState.Popup(['Enter', 'Copy', 'Move', 'Delete'],
                                                                          [self._enter, self._copy, self._move,
                                                                           self._delete])
            else:
                self.__active_directory.popup = self.DirectoryState.Popup(['Copy', 'Move', 'Delete'],
                                                                          [self._copy, self._move, self._delete])

    @override
    def on_key_b(self):
        if self.__active_directory.error_message is not None:
            self.__active_directory.remove_error_message()
        elif self.__active_directory.popup is not None:
            self.__active_directory.remove_popup()
        else:
            path = os.path.abspath(os.path.join(self.__active_directory.directory, '..'))
            if os.path.isdir(path):
                old_path = self.__active_directory.directory
                self.__active_directory.directory = path
                try:
                    index = next(
                        i for i, f in enumerate(self.__active_directory.files) if os.path.join(path, f) == old_path)
                    self.__active_directory.selected_index = index
                except StopIteration:
                    pass
