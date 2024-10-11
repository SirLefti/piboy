from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.data import ConnectionStatus


@dataclass
class EnvironmentData:
    temperature: float
    pressure: float
    humidity: float


class EnvironmentDataProvider(ABC):
    """Data provider for environmental data."""

    @abstractmethod
    def get_environment_data(self) -> EnvironmentData:
        """Returns an object containing temperature, pressure and humidity."""
        raise NotImplementedError

    @abstractmethod
    def get_device_status(self) -> ConnectionStatus:
        """Returns the connection status of the hardware module."""
        raise NotImplementedError
