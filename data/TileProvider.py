from abc import ABC, abstractmethod
from typing import Iterable
from PIL import Image


class TileInfo:
    """Representation of a map tile."""

    def __init__(self, top_left: tuple[float, float], bottom_right: tuple[float, float], image: Image.Image):
        self.__top_left = top_left
        self.__bottom_right = bottom_right
        self.__image = image

    @property
    def top_left(self) -> tuple[float, float]:
        """Decimal degrees of the top left corner of the tile"""
        return self.__top_left

    @property
    def bottom_right(self) -> tuple[float, float]:
        """Decimal degrees of the bottom right corner of the tile"""
        return self.__bottom_right

    @property
    def image(self) -> Image.Image:
        """Tile image"""
        return self.__image


class TileProvider(ABC):
    """Data provider for map tiles."""

    @abstractmethod
    def get_tile(self, lat: float, lon: float, zoom: int, size: tuple[int, int] = (256, 256), x_offset: int = 0,
                 y_offset: int = 0) -> TileInfo:
        """
        Returns a tile object for the given decimal degrees and zoom level with the requested position being in the
        center.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def zoom_range(self) -> Iterable[int]:
        """Returns a range of supported zoom levels."""
        raise NotImplementedError
