from abc import ABC, abstractmethod
from dataclasses import dataclass


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
