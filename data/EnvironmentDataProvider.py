from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.data import DeviceStatus


@dataclass
class EnvironmentData:
    temperature: float
    pressure: float
    humidity: float


class EnvironmentDataProvider(ABC):
    """Data provider for environmental data."""

    @abstractmethod
    def get_environment_data(self) -> EnvironmentData | None:
        """Returns an object containing temperature, pressure and humidity."""
        raise NotImplementedError

    @abstractmethod
    def get_device_status(self) -> DeviceStatus:
        """Returns the device status of the hardware module."""
        raise NotImplementedError
