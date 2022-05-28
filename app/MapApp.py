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
        font = config.FONT_STANDARD
        lat, lon = self.__location_provider.get_location()
        size = (config.RESOLUTION[0] - 2 * config.APP_SIDE_OFFSET, config.RESOLUTION[1] - config.APP_TOP_OFFSET - config.APP_BOTTOM_OFFSET)
        tile = self.__tile_provider.get_tile(lat, lon, self.__zoom, size=size)
        image.paste(tile, left_top)
        draw.text(left_top, f'lat: {lat}°, lon: {lon}°', config.BACKGROUND, font=font)
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
        pass

    def on_key_b(self):
        pass
