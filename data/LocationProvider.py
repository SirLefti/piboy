from abc import ABC, abstractmethod


class LocationProvider(ABC):
    """Data provider for a geo location."""

    @abstractmethod
    def get_location(self) -> tuple[float, float]:
        """Returns a location as a tuple of decimal degrees to north and east."""
        raise NotImplementedError


class LocationException(Exception):

    def __init__(self, message: str, inner_exception: Exception):
        self.message = message
        self.inner_exception = inner_exception
