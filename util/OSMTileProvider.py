from util.BaseTileProvider import BaseTileProvider, TileInfo
from typing import Tuple
from PIL import Image
import os
import requests
import math


class OSMTileProvider(BaseTileProvider):

    def get_tile(self, lat: float, lon: float, zoom: int, size: Tuple[int, int] = (256, 256)) -> TileInfo:
        tile_cache = '.tiles'
        cache_template = '{zoom}-{x}-{y}.png'
        x_tile, y_tile = self._deg_to_num(lat, lon, zoom)

        if not os.path.exists(tile_cache):
            os.mkdir(tile_cache)

        tile_path = os.path.join(tile_cache, cache_template.format(zoom=zoom, x=x_tile, y=y_tile))
        if os.path.exists(tile_path):
            img = Image.open(tile_path)
            return TileInfo(self._num_to_deg(x_tile, y_tile, zoom), self._num_to_deg(x_tile + 1, y_tile + 1, zoom),
                            self._resize(img, size))
        else:
            response = requests.get(f'https://tile.openstreetmap.org/{zoom}/{x_tile}/{y_tile}.png')
            if response.status_code == 200:
                with open(tile_path, 'wb') as f:
                    f.write(response.content)
                img = Image.open(tile_path)
                return TileInfo(self._num_to_deg(x_tile, y_tile, zoom), self._num_to_deg(x_tile + 1, y_tile + 1, zoom),
                                self._resize(img, size))
            else:
                raise ValueError(f'Fetching OSM tile failed ({response.status_code})')

    @classmethod
    def _resize(cls, img: Image, size: Tuple[int, int]) -> Image:
        if img.size == size:
            return img
        old_x, old_y = img.size
        new_x, new_y = size
        scale = max(new_x / old_x, new_y / old_y)
        resized = img.resize((int(old_x * scale), int(old_y * scale)), Image.ANTIALIAS)
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
