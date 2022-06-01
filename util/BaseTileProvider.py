from abc import ABC, abstractmethod
from typing import Tuple, Iterable
from PIL import Image


class TileInfo:

    def __init__(self, top_left: Tuple[float, float], bottom_right: Tuple[float, float], image: Image):
        self.__top_left = top_left
        self.__bottom_right = bottom_right
        self.__image = image

    @property
    def top_left(self) -> Tuple[float, float]:
        return self.__top_left

    @property
    def bottom_right(self) -> Tuple[float, float]:
        return self.__bottom_right

    @property
    def image(self) -> Image:
        return self.__image


class BaseTileProvider(ABC):

    def get_tile(self, lat: float, lon: float, zoom: int, size: Tuple[int, int] = (256, 256), x_offset: int = 0,
                 y_offset: int = 0) -> TileInfo:
        raise NotImplementedError

    @property
    @abstractmethod
    def zoom_range(self) -> Iterable[int]:
        raise NotImplementedError
