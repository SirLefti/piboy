from abc import ABC, abstractmethod

from core.data import ConnectionStatus


class BatteryStatusProvider(ABC):
    """Data provider for the state of charge of the battery."""

    @abstractmethod
    def get_state_of_charge(self) -> float:
        """Returns state of charge as a float between 0 and 1."""
        raise NotImplementedError

    @abstractmethod
    def get_device_status(self) -> ConnectionStatus:
        """Returns the connection status of the hardware module."""
        raise NotImplementedError
