from abc import ABC, abstractmethod
from typing import Tuple


class BaseLocationProvider(ABC):

    @abstractmethod
    def get_location(self) -> Tuple[float, float]:
        raise NotImplementedError
