from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float


class LocationProvider(ABC):
    """Data provider for a geo location."""

    @abstractmethod
    def get_location(self) -> Location:
        """Returns a location."""
        raise NotImplementedError


class LocationException(Exception):

    def __init__(self, message: str, inner_exception: Optional[Exception] = None):
        self.message = message
        self.inner_exception = inner_exception
