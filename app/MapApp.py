from app.BaseApp import SelfUpdatingApp
from interface.BaseInterface import BaseInterface
from util.BaseLocationProvider import BaseLocationProvider
from util.BaseTileProvider import BaseTileProvider
from enum import Enum
from abc import ABC
from typing import Callable, Tuple, List
from PIL import Image, ImageDraw, ImageOps
import os.path
import config


class MapApp(SelfUpdatingApp):
    __SCROLL_FACTOR = 10
    __CONTROL_SIZE = 30
    __CONTROL_PADDING = 4

    class Control(ABC):

        class SelectionState(Enum):
            NONE = 0, config.ACCENT_DARK, config.BACKGROUND
            FOCUSSED = 1, config.ACCENT, config.BACKGROUND
            SELECTED = 2, config.BACKGROUND, config.ACCENT

            def __new__(cls, *args, **kwargs):
                obj = object.__new__(cls)
                obj._value_ = args[0]
                return obj

            # skip first argument, it is the value for the enum
            def __init__(self, _, color: Tuple[int, int, int], background_color: Tuple[int, int, int]):
                self.__color = color
                self.__background_color = background_color

            @property
            def color(self):
                return self.__color

            @property
            def background_color(self):
                return self.__background_color

        def __init__(self, icon_bitmap: Image,
                     on_select: Callable[[], None] = None, on_deselect: Callable[[], None] = None,
                     on_key_left: Callable[[], None] = None, on_key_right: Callable[[], None] = None,
                     on_key_up: Callable[[], None] = None, on_key_down: Callable[[], None] = None,
                     instant_action=False, initial_state=SelectionState.NONE):
            self.__icon_bitmap = icon_bitmap
            self.__on_select = on_select
            self.__on_deselect = on_deselect
            self.__on_key_left = on_key_left
            self.__on_key_right = on_key_right
            self.__on_key_up = on_key_up
            self.__on_key_down = on_key_down
            self.__instant_action = instant_action  # instant actions won't get the SELECTED flag
            self.__selection_state = initial_state

        def on_key_left(self):
            if self.__on_key_left is not None:
                self.__on_key_left()

        def on_key_right(self):
            if self.__on_key_right is not None:
                self.__on_key_right()

        def on_key_up(self):
            if self.__on_key_up is not None:
                self.__on_key_up()

        def on_key_down(self):
            if self.__on_key_down is not None:
                self.__on_key_down()

        def on_select(self):
            """When pressing button A"""
            if not self.__instant_action:
                self.__selection_state = self.SelectionState.SELECTED
            if self.__on_select is not None:
                self.__on_select()

        def on_deselect(self):
            """When pressing button B"""
            if not self.__instant_action:
                self.__selection_state = self.SelectionState.FOCUSSED
            if self.__on_deselect is not None:
                self.__on_deselect()

        def on_focus(self):
            """When moving selection on this control"""
            self.__selection_state = self.SelectionState.FOCUSSED

        def on_blur(self):
            """When moving selection away from this control"""
            self.__selection_state = self.SelectionState.NONE

        def draw(self, draw: ImageDraw, left_top: Tuple[int, int]):
            width, height = self.__icon_bitmap.size
            left, top = left_top
            draw.rectangle(left_top + (left + width - 1, top + height - 1),
                           fill=self.__selection_state.background_color)
            draw.bitmap(left_top, self.__icon_bitmap, fill=self.__selection_state.color)

        def is_selected(self) -> bool:
            return self.__selection_state == self.SelectionState.SELECTED

    def __init__(self, interface: BaseInterface, draw_callback: Callable[[], None],
                 location_provider: BaseLocationProvider, tile_provider: BaseTileProvider):
        super().__init__(interface, self.__update_location)
        self.__draw_callback = draw_callback
        self.__location_provider = location_provider
        self.__tile_provider = tile_provider
        self.__zoom = 15
        self.__x_offset = 0
        self.__y_offset = 0
        self.__position = self.__location_provider.get_location()

        resources_path = 'resources'
        minus_icon = Image.open(os.path.join(resources_path, 'minus.png')).convert('1')
        plus_icon = Image.open(os.path.join(resources_path, 'plus.png')).convert('1')
        move_icon = Image.open(os.path.join(resources_path, 'move.png')).convert('1')
        focus_icon = Image.open(os.path.join(resources_path, 'focus.png')).convert('1')

        def zoom_in():
            if self.__zoom + 1 in self.__tile_provider.zoom_range:
                self.__zoom = self.__zoom + 1

        def zoom_out():
            if self.__zoom - 1 in self.__tile_provider.zoom_range:
                self.__zoom = self.__zoom - 1

        def reset_offset():
            self.__x_offset = 0
            self.__y_offset = 0

        def move_left():
            self.__x_offset -= 1

        def move_right():
            self.__x_offset += 1

        def move_up():
            self.__y_offset -= 1

        def move_down():
            self.__y_offset += 1

        self.__controls: List[MapApp.Control] = [
            self.Control(ImageOps.invert(minus_icon), on_select=zoom_out, instant_action=True,
                         initial_state=self.Control.SelectionState.FOCUSSED),
            self.Control(ImageOps.invert(plus_icon), on_select=zoom_in, instant_action=True),
            self.Control(ImageOps.invert(move_icon), on_key_left=move_left, on_key_right=move_right,
                         on_key_up=move_up, on_key_down=move_down,
                         on_select=self.stop_updating, on_deselect=self.start_updating),
            self.Control(ImageOps.invert(focus_icon), on_select=reset_offset, instant_action=True)
        ]
        self.__focussed_control = 0

    @property
    def title(self) -> str:
        return 'MAP'

    @property
    def refresh_time(self) -> float:
        return 10.0

    def __update_location(self):
        if self.__x_offset == 0 and self.__y_offset == 0:
            self.__position = self.__location_provider.get_location()
            self.__draw_callback()

    def draw(self, image: Image) -> Image:
        draw = ImageDraw.Draw(image)
        left_top = (config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET)
        width, height = config.RESOLUTION
        side_tab_width = 120
        side_tab_padding = 5
        line_height = 20
        font = config.FONT_STANDARD

        lat, lon = self.__position
        size = (width - 2 * config.APP_SIDE_OFFSET - side_tab_width,
                height - config.APP_TOP_OFFSET - config.APP_BOTTOM_OFFSET)
        tile = self.__tile_provider.get_tile(lat, lon, self.__zoom, size=size,
                                             x_offset=self.__x_offset * self.__SCROLL_FACTOR,
                                             y_offset=self.__y_offset * self.__SCROLL_FACTOR)
        image.paste(tile.image, left_top)

        # calculate the relative position of the current location on the tile, because the tile is not centered around
        # the given location. It even works with resized and cropped tiles, as long as the center stays the center
        if self.__x_offset * self.__SCROLL_FACTOR + int(size[0] / 2) in range(size[0]) \
                and self.__y_offset * self.__SCROLL_FACTOR + int(size[1] / 2) in range(size[1]):
            tile_top, tile_left = tile.top_left
            tile_bottom, tile_right = tile.bottom_right
            x_position = (lon - tile_left) / (tile_right - tile_left)
            y_position = (lat - tile_top) / (tile_bottom - tile_top)
            marker_center = (left_top[0] + size[0] * x_position - self.__x_offset * self.__SCROLL_FACTOR,
                             left_top[1] + size[1] * y_position - self.__y_offset * self.__SCROLL_FACTOR)
            marker_size = 20
            draw.polygon([marker_center,
                          (marker_center[0] - int(marker_size / 2), marker_center[1] - marker_size),
                          (marker_center[0] + int(marker_size / 2), marker_center[1] - marker_size)],
                         fill=config.ACCENT_DARK)
        else:
            # TODO draw marker/arrow where location is
            pass

        # draw location info
        cursor = (left_top[0] + size[0] + side_tab_padding, left_top[1])
        draw.text(cursor, 'lat: {:.4f}°'.format(lat), config.ACCENT, font=font)
        cursor = (cursor[0], cursor[1] + line_height)
        draw.text(cursor, 'lon: {:.4f}°'.format(lon), config.ACCENT, font=font)
        cursor = (cursor[0], cursor[1] + line_height)
        draw.text(cursor, f'zoom: {self.__zoom}x', config.ACCENT, font=font)
        if self.__x_offset != 0 or self.__y_offset != 0:
            cursor = (cursor[0], cursor[1] + line_height)
            draw.text(cursor, f'x: {self.__x_offset}, y: {self.__y_offset}', config.ACCENT, font=font)

        # draw controls
        cursor = (left_top[0] + size[0] - self.__CONTROL_SIZE - self.__CONTROL_PADDING,
                  left_top[1] + size[1] - self.__CONTROL_SIZE - self.__CONTROL_PADDING)
        for control in self.__controls:
            control.draw(draw, cursor)
            cursor = (cursor[0], cursor[1] - self.__CONTROL_SIZE - 2 * self.__CONTROL_PADDING)
        return image

    def on_key_left(self):
        if self.__controls[self.__focussed_control].is_selected():
            self.__controls[self.__focussed_control].on_key_left()

    def on_key_right(self):
        if self.__controls[self.__focussed_control].is_selected():
            self.__controls[self.__focussed_control].on_key_right()

    def on_key_up(self):
        if self.__controls[self.__focussed_control].is_selected():
            self.__controls[self.__focussed_control].on_key_up()
        else:
            self.__controls[self.__focussed_control].on_blur()
            self.__focussed_control = min(self.__focussed_control + 1, len(self.__controls) - 1)
            self.__controls[self.__focussed_control].on_focus()

    def on_key_down(self):
        if self.__controls[self.__focussed_control].is_selected():
            self.__controls[self.__focussed_control].on_key_down()
        else:
            self.__controls[self.__focussed_control].on_blur()
            self.__focussed_control = max(self.__focussed_control - 1, 0)
            self.__controls[self.__focussed_control].on_focus()

    def on_key_a(self):
        self.__controls[self.__focussed_control].on_select()

    def on_key_b(self):
        self.__controls[self.__focussed_control].on_deselect()
