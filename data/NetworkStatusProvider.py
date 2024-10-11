from abc import ABC, abstractmethod

from core.data import ConnectionStatus


class NetworkStatusProvider(ABC):
    """Data provider for the network status."""

    @abstractmethod
    def get_status(self) -> ConnectionStatus:
        """Returns the network connection status."""
        raise NotImplementedError
