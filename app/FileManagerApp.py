from typing import Tuple
from app.BaseApp import BaseApp
from PIL import ImageDraw, ImageFont
import config
import os


class FileManagerApp(BaseApp):

    def __init__(self):
        self.__left_directory = os.path.expanduser('~')
        self.__right_directory = os.path.expanduser('~')
        self.__selected_tab = 0  # 0 for left, 1 for right
        self.__left_selected_index = 0
        self.__right_selected_index = 0
        self.__left_top_index = 0
        self.__right_top_index = 0
        pass

    @property
    def title(self) -> str:
        return "INV"

    @staticmethod
    def __draw_directory(draw: ImageDraw, left_top: Tuple[int, int], right_bottom: Tuple[int, int],
                         directory: str, selected_index: int, top_index: int, is_selected: bool) -> int:
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
        draw.text((left + side_padding, top), directory, config.ACCENT, font=font)

        cursor = (left, top + line_height)
        content = os.listdir(directory)
        entries = len(content)
        max_entries = int((bottom - cursor[1]) / line_height)
        max_entries -= 1 if entries > max_entries else 0  # reduce max shown entries to show the ... line if needed
        if entries > max_entries:  # not all entries will fit in the view
            if selected_index < top_index:
                top_index = selected_index
            elif selected_index not in range(top_index, top_index + max_entries):
                top_index = selected_index - max_entries + 1
        else:  # all entries will fit, set top_index to 0
            top_index = 0

        for index, file in enumerate(sorted([f for f in content if not f.startswith('.')], key=str.lower)[top_index:]):
            cursor_x, cursor_y = cursor
            index += top_index  # pad index if entries are skipped
            if selected_index == index and is_selected:
                draw.rectangle((left, cursor_y, right, cursor_y + line_height), fill=config.BACKGROUND)

            start = (left + symbol_padding, cursor_y + symbol_padding)
            end = (left + symbol_padding + symbol_dimensions, cursor_y + symbol_padding + symbol_dimensions)
            if end[1] > bottom - line_height:
                draw.text((cursor_x + side_padding, cursor_y), '...', config.ACCENT, font=font)
                break

            if os.path.isfile(os.path.join(directory, file)):
                draw.ellipse(start + end, fill=config.ACCENT)  # draw circle for file
            else:
                draw.rectangle(start + end, fill=config.ACCENT)  # draw square for directory
            draw.text((cursor_x + symbol_dimensions + 2 * symbol_padding, cursor_y), file, config.ACCENT, font=font)
            cursor = (cursor_x, cursor_y + line_height)

        return top_index

    def draw(self, draw: ImageDraw) -> ImageDraw:
        width, height = config.INTERFACE.resolution
        # font = ImageFont.truetype(config.FONT, 14)

        left_top = (config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET)
        right_bottom = (int(width / 2), height - config.APP_BOTTOM_OFFSET)
        self.__left_top_index = self.__draw_directory(draw, left_top, right_bottom, self.__left_directory,
                                                      self.__left_selected_index, self.__left_top_index,
                                                      is_selected=self.__selected_tab == 0)

        left_top = (int(width / 2), config.APP_TOP_OFFSET)
        right_bottom = (width - config.APP_SIDE_OFFSET, height - config.APP_BOTTOM_OFFSET)
        self.__right_top_index = self.__draw_directory(draw, left_top, right_bottom, self.__right_directory,
                                                       self.__right_selected_index, self.__right_top_index,
                                                       is_selected=self.__selected_tab == 1)

        # split line
        start = (width / 2 - 1, config.APP_TOP_OFFSET)
        end = (width / 2, height - config.APP_BOTTOM_OFFSET)
        draw.rectangle(start + end, fill=config.ACCENT)

        return draw

    def on_key_left(self):
        self.__selected_tab ^= 1  # flip bit to change tab

    def on_key_up(self):
        if self.__selected_tab:
            self.__right_selected_index -= 1
            if self.__right_selected_index < 0:
                self.__right_selected_index = 0
        else:
            self.__left_selected_index -= 1
            if self.__left_selected_index < 0:
                self.__left_selected_index = 0

    def on_key_right(self):
        self.__selected_tab ^= 1  # flip bit to change tab

    def on_key_down(self):
        # TODO check for out of bounds here as well
        if self.__selected_tab:
            self.__right_selected_index += 1
        else:
            self.__left_selected_index += 1

    def on_key_a(self):
        pass

    def on_key_b(self):
        pass
