import os
from typing import Tuple, List
from PIL import ImageDraw, ImageFont
import config
from app.BaseApp import BaseApp


class FileManagerApp(BaseApp):

    class DirectoryState:

        def __init__(self):
            self.__directory = os.path.expanduser('~')
            self.__top_index = 0
            self.__selected_index = 0

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

        @property
        def entries(self) -> int:
            return len(self.files)

        @property
        def files(self) -> List[str]:
            return sorted([f for f in os.listdir(self.__directory) if not f.startswith('.')], key=str.lower)

    def __init__(self):
        self.__left_directory = self.DirectoryState()
        self.__right_directory = self.DirectoryState()
        self.__selected_tab = 0  # 0 for left, 1 for right
        pass

    @property
    def title(self) -> str:
        return "INV"

    @staticmethod
    def __draw_directory(draw: ImageDraw, left_top: Tuple[int, int], right_bottom: Tuple[int, int],
                         state: DirectoryState, is_selected: bool) -> None:
        """Draws the given directory to the given ImageDraw and returns the new top_index."""
        line_height = 20  # height of a line entry in the directory
        side_padding = 3  # padding to the side of the directory background
        symbol_dimensions = 10  # size of symbol entry
        symbol_padding = (line_height - symbol_dimensions) / 2  # space around symbol
        left, top = left_top  # unpacking top left anchor point
        right, bottom = right_bottom  # unpacking bottom right anchor point
        font = ImageFont.truetype(config.FONT, 14)

        # draw background if this directory is selected
        if is_selected:
            draw.rectangle(left_top + right_bottom, fill=config.ACCENT_DARK)
        draw.text((left + side_padding, top), state.directory, config.ACCENT, font=font)

        cursor = (left, top + line_height)
        content = os.listdir(state.directory)
        entries = len(content)
        max_entries = int((bottom - cursor[1]) / line_height)
        max_entries -= 1 if entries > max_entries else 0  # reduce max shown entries to show the ... line if needed
        if entries > max_entries:  # not all entries will fit in the view
            if state.selected_index < state.top_index:
                state.top_index = state.selected_index
            elif state.selected_index not in range(state.top_index, state.top_index + max_entries):
                state.top_index = state.selected_index - max_entries + 1
        else:  # all entries will fit, set top_index to 0
            state.top_index = 0

        for index, file in enumerate(state.files[state.top_index:]):
            cursor_x, cursor_y = cursor
            index += state.top_index  # pad index if entries are skipped
            if state.selected_index == index and is_selected:
                draw.rectangle((left, cursor_y, right, cursor_y + line_height), fill=config.BACKGROUND)

            start = (left + symbol_padding, cursor_y + symbol_padding)
            end = (left + symbol_padding + symbol_dimensions, cursor_y + symbol_padding + symbol_dimensions)
            if end[1] > bottom - line_height:
                draw.text((cursor_x + side_padding, cursor_y), '...', config.ACCENT, font=font)
                break

            if os.path.isfile(os.path.join(state.directory, file)):
                draw.ellipse(start + end, fill=config.ACCENT)  # draw circle for file
            else:
                draw.rectangle(start + end, fill=config.ACCENT)  # draw square for directory

            while draw.textsize(file, font=font)[0] > right - left - symbol_dimensions - 2 * symbol_padding:
                file = file[:-1]  # cut off last char until it fits
            draw.text((cursor_x + symbol_dimensions + 2 * symbol_padding, cursor_y), file, config.ACCENT, font=font)
            cursor = (cursor_x, cursor_y + line_height)

    def draw(self, draw: ImageDraw) -> ImageDraw:
        width, height = config.INTERFACE.resolution
        # font = ImageFont.truetype(config.FONT, 14)

        left_top = (config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET)
        right_bottom = (int(width / 2), height - config.APP_BOTTOM_OFFSET)
        self.__draw_directory(draw, left_top, right_bottom, self.__left_directory, is_selected=self.__selected_tab == 0)

        left_top = (int(width / 2), config.APP_TOP_OFFSET)
        right_bottom = (width - config.APP_SIDE_OFFSET, height - config.APP_BOTTOM_OFFSET)
        self.__draw_directory(draw, left_top, right_bottom, self.__right_directory, is_selected=self.__selected_tab == 1)

        # split line
        start = (width / 2 - 1, config.APP_TOP_OFFSET)
        end = (width / 2, height - config.APP_BOTTOM_OFFSET)
        draw.rectangle(start + end, fill=config.ACCENT)

        return draw

    def on_key_left(self):
        self.__selected_tab ^= 1  # flip bit to change tab

    def on_key_up(self):
        if self.__selected_tab:
            self.__right_directory.selected_index = max(self.__right_directory.selected_index - 1, 0)
        else:
            self.__left_directory.selected_index = max(self.__left_directory.selected_index - 1, 0)

    def on_key_right(self):
        self.__selected_tab ^= 1  # flip bit to change tab

    def on_key_down(self):
        if self.__selected_tab:
            self.__right_directory.selected_index = min(self.__right_directory.selected_index + 1,
                                                        self.__right_directory.entries - 1)
        else:
            self.__left_directory.selected_index = min(self.__left_directory.selected_index + 1,
                                                       self.__left_directory.entries - 1)

    def on_key_a(self):
        pass

    def on_key_b(self):
        pass
