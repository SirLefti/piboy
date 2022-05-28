from abc import ABC
from typing import Tuple
from PIL import Image


class BaseTileProvider(ABC):

    def get_tile(self, lat: float, lon: float, zoom: int, size: Tuple[int, int] = (256, 256)) -> Image:
        raise NotImplementedError
