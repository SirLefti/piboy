from abc import ABC, abstractmethod
from typing import Tuple


class LocationProvider(ABC):

    @abstractmethod
    def get_location(self) -> Tuple[float, float]:
        raise NotImplementedError
