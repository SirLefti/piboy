from data.TileProvider import TileProvider, TileInfo
from typing import Tuple, Iterable
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from requests.exceptions import ConnectionError
import os
import requests
import math
import time


class OSMTileProvider(TileProvider):

    __CACHE_DURATION = 1000 * 60 * 60 * 24 * 365  # one year in ms
    __OSM_TILE_SIZE = (256, 256)  # size of a tile image from OSM

    def __init__(self, background: Tuple[int, int, int], color: Tuple[int, int, int], font: ImageFont):
        self.__background = background
        self.__color = color
        self.__font = font

    @property
    def zoom_range(self) -> Iterable[int]:
        return range(0, 20)

    def get_tile(self, lat: float, lon: float, zoom: int, size: Tuple[int, int] = (256, 256), x_offset: int = 0,
                 y_offset: int = 0) -> TileInfo:
        x_tile, y_tile = self._deg_to_num(lat, lon, zoom)
        tile: Image
        try:
            tile = self._fetch_tile(zoom, x_tile, y_tile)
        except (ValueError, FileNotFoundError, ConnectionError, UnidentifiedImageError):
            tile = self._get_placeholder_tile()
        tile_width, tile_height = tile.size
        target_width, target_height = size

        # calculate the relative position of the current location on the tile, because the tile is not centered around
        # the given location.
        tile_top_deg, tile_left_deg = self._num_to_deg(x_tile, y_tile, zoom)
        tile_bottom_deg, tile_right_deg = self._num_to_deg(x_tile + 1, y_tile + 1, zoom)
        x_position = int((lon - tile_left_deg) / (tile_right_deg - tile_left_deg) * tile_width) + x_offset
        y_position = int((lat - tile_top_deg) / (tile_bottom_deg - tile_top_deg) * tile_height) + y_offset

        # calculate the total tiles to be fetched
        left_tiles = int((target_width / 2 - x_position + tile_width) / tile_width)
        right_tiles = int((target_width / 2 - (tile_width - x_position) + tile_width) / tile_width)
        top_tiles = int((target_height / 2 - y_position + tile_height) / tile_height)
        bottom_tiles = int((target_height / 2 - (tile_height - y_position) + tile_height) / tile_height)

        grid: list[list[Image]] = [
            [None for _ in range(top_tiles + 1 + bottom_tiles)] for _ in range(left_tiles + 1 + right_tiles)
        ]
        grid[left_tiles][top_tiles] = tile

        for x, row in enumerate(grid):
            for y, _ in enumerate(row):
                if y_tile - top_tiles + y < 0 or y_tile - top_tiles + y == math.pow(2, zoom):
                    # empty image if tile ends on top or bottom and there is no further tile
                    grid[x][y] = Image.new('RGB', size, self.__background)
                else:
                    try:
                        grid[x][y] = self._fetch_tile(zoom, (x_tile - left_tiles + x) % int(math.pow(2, zoom)),
                                                      (y_tile - top_tiles + y) % int(math.pow(2, zoom)))
                    except (ValueError, FileNotFoundError, ConnectionError, UnidentifiedImageError):
                        grid[x][y] = grid[x][y] = self._get_placeholder_tile()

        merged_tile = Image.new('RGB', (len(grid) * tile_width, len(grid[0]) * tile_height), (255, 255, 255))
        for row_index, row in enumerate(grid):
            for patch_index, patch in enumerate(row):
                merged_tile.paste(patch, (row_index * tile_width, patch_index * tile_height))

        center_x = int(tile_width * left_tiles + x_position)
        center_y = int(tile_height * top_tiles + y_position)
        cropped_left = center_x - int(target_width / 2)
        cropped_top = center_y - int(target_height / 2)
        cropped_tile = merged_tile.crop((cropped_left, cropped_top,
                                         cropped_left + target_width, cropped_top + target_height))
        width_deg = (tile_right_deg - tile_left_deg) * (tile_width / target_width)
        height_deg = (tile_bottom_deg - tile_top_deg) * (tile_height / target_height)
        top_left = lat - (height_deg / 2), lon - (width_deg / 2)
        bottom_right = lat + (height_deg / 2), lon + (width_deg / 2)
        return TileInfo(top_left, bottom_right, cropped_tile)

    def _get_placeholder_tile(self) -> Image:
        font = self.__font
        tile = Image.new('RGB', self.__OSM_TILE_SIZE, self.__background)
        text_w, text_h = font.getbbox('?')[-2:]
        tile_w, tile_h = tile.size
        draw = ImageDraw.Draw(tile)
        draw.rectangle((0, 0) + self.__OSM_TILE_SIZE, fill=self.__background, outline=self.__color, width=1)
        draw.text((tile_w / 2 - text_w / 2, tile_h / 2 - text_h / 2), '?', font=font)
        return tile

    @classmethod
    def _fetch_tile(cls, zoom: int, x_tile: int, y_tile: int) -> Image:
        """Fetches the requested tile either from cache or from OSM tile API"""
        tile_cache = '.tiles'
        cache_template = '{zoom}-{x}-{y}.png'
        if not os.path.isdir(tile_cache):
            os.mkdir(tile_cache)
        tile_path = os.path.join(tile_cache, cache_template.format(zoom=zoom, x=x_tile, y=y_tile))
        if os.path.isfile(tile_path) and time.time() - os.path.getmtime(tile_path) < cls.__CACHE_DURATION:
            return Image.open(tile_path)
        else:
            headers = {
                'User-Agent': 'piboy'
            }
            response = requests.get(f'https://tile.openstreetmap.org/{zoom}/{x_tile}/{y_tile}.png', headers=headers)
            if response.status_code == 200:
                with open(tile_path, 'wb') as f:
                    f.write(response.content)
                return Image.open(tile_path)
            else:
                raise ValueError(f'Fetching OSM tile ({zoom}-{x_tile}-{y_tile}) failed ({response.status_code})')

    @classmethod
    def _resize(cls, img: Image, size: Tuple[int, int]) -> Image:
        if img.size == size:
            return img
        old_x, old_y = img.size
        new_x, new_y = size
        scale = max(new_x / old_x, new_y / old_y)
        resized = img.resize((int(old_x * scale), int(old_y * scale)), Image.LANCZOS)
        res_x, res_y = resized.size
        offset_x = int((res_x - new_x) / 2)
        offset_y = int((res_y - new_y) / 2)
        return resized.crop((offset_x, offset_y, offset_x + new_x, offset_y + new_y))

    @classmethod
    def _deg_to_num(cls, lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
        """Code from: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x_tile = int((lon_deg + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    @classmethod
    def _num_to_deg(cls, x_tile: int, y_tile: int, zoom: int) -> Tuple[float, float]:
        """Code from: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames"""
        n = 2.0 ** zoom
        lon_deg = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg
