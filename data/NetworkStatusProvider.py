from abc import ABC, abstractmethod
from enum import Enum


class NetworkStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2

class NetworkStatusProvider(ABC):
    """Data provider for the network status."""

    @abstractmethod
    def get_status(self) -> NetworkStatus:
        raise NotImplementedError
