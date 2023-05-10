from abc import ABC, abstractmethod
from typing import Tuple


class LocationProvider(ABC):

    @abstractmethod
    def get_location(self) -> Tuple[float, float]:
        raise NotImplementedError


class LocationException(Exception):

    def __init__(self, message: str, inner_exception: Exception):
        self.message = message
        self.inner_exception = inner_exception
