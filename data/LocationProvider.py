from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float


class LocationStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2


class LocationProvider(ABC):
    """Data provider for a geo location."""

    @abstractmethod
    def get_location(self) -> Location:
        """Returns a location."""
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> LocationStatus:
        """Returns the connection status of the location provider."""
        raise NotImplementedError


class LocationException(Exception):

    def __init__(self, message: str, inner_exception: Optional[Exception] = None):
        self.message = message
        self.inner_exception = inner_exception
