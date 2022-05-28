from app.BaseApp import BaseApp
from util.BaseLocationProvider import BaseLocationProvider
from util.BaseTileProvider import BaseTileProvider
from PIL import Image, ImageDraw
import config


class MapApp(BaseApp):

    def __init__(self, location_provider: BaseLocationProvider, tile_provider: BaseTileProvider):
        self.__location_provider = location_provider
        self.__tile_provider = tile_provider
        self.__zoom = 15

    @property
    def title(self) -> str:
        return 'MAP'

    def draw(self, image: Image) -> Image:
        draw = ImageDraw.Draw(image)
        left_top = (config.APP_SIDE_OFFSET, config.APP_TOP_OFFSET)
        width, height = config.RESOLUTION
        side_tab_width = 120
        side_tab_padding = 5
        line_height = 20
        font = config.FONT_STANDARD

        lat, lon = self.__location_provider.get_location()
        size = (width - 2 * config.APP_SIDE_OFFSET - side_tab_width,
                height - config.APP_TOP_OFFSET - config.APP_BOTTOM_OFFSET)
        tile = self.__tile_provider.get_tile(lat, lon, self.__zoom, size=size)
        image.paste(tile.image, left_top)

        # calculate the relative position of the current location on the tile, because the tile is not centered around
        # the given location. It even works with resized and cropped tiles, as long as the center stays the center
        tile_top, tile_left = tile.top_left
        tile_bottom, tile_right = tile.bottom_right
        x_position = (lon - tile_left) / (tile_right - tile_left)
        y_position = (lat - tile_top) / (tile_bottom - tile_top)
        marker_center = (left_top[0] + size[0] * x_position, left_top[1] + size[1] * y_position)
        marker_size = 20
        draw.polygon([marker_center,
                      (marker_center[0] - int(marker_size / 2), marker_center[1] - marker_size),
                      (marker_center[0] + int(marker_size / 2), marker_center[1] - marker_size)],
                     fill=config.ACCENT_DARK)

        cursor = (left_top[0] + size[0] + side_tab_padding, left_top[1])
        draw.text(cursor, f'lat: {lat}°', config.ACCENT, font=font)
        cursor = (cursor[0], cursor[1] + line_height)
        draw.text(cursor, f'lon: {lon}°', config.ACCENT, font=font)
        cursor = (cursor[0], cursor[1] + line_height)
        draw.text(cursor, f'zoom: {self.__zoom}x', config.ACCENT, font=font)
        return image

    def on_key_left(self):
        pass

    def on_key_right(self):
        pass

    def on_key_up(self):
        pass

    def on_key_down(self):
        pass

    def on_key_a(self):
        if self.__zoom + 1 in self.__tile_provider.zoom_range:
            self.__zoom = self.__zoom + 1

    def on_key_b(self):
        if self.__zoom - 1 in self.__tile_provider.zoom_range:
            self.__zoom = self.__zoom - 1
