from abc import ABC, abstractmethod

from core.data import DeviceStatus


class NetworkStatusProvider(ABC):
    """Data provider for the network status."""

    @abstractmethod
    def get_status(self) -> DeviceStatus:
        """Returns the network connection status."""
        raise NotImplementedError
