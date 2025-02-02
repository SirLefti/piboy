from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from core.data import DeviceStatus


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

    @abstractmethod
    def get_device_status(self) -> DeviceStatus:
        """Returns the device status of the hardware module."""
        raise NotImplementedError


class LocationException(Exception):

    def __init__(self, message: str, inner_exception: Optional[Exception] = None):
        self.message = message
        self.inner_exception = inner_exception
