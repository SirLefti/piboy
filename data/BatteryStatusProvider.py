from abc import ABC, abstractmethod


class BatteryStatusProvider(ABC):
    """Data provider for the state of charge of the battery."""

    @abstractmethod
    def get_state_of_charge(self) -> float:
        """Returns state of charge as a float between 0 and 1."""
        raise NotImplementedError
