import random

from core.data import ConnectionStatus
from core.decorator import override
from data.EnvironmentDataProvider import EnvironmentData, EnvironmentDataProvider


class FakeEnvironmentDataProvider(EnvironmentDataProvider):

    def __init__(self, fake_temperature: float = 20.5, fake_pressure: float = 1013.25, fake_humidity: float = .45):
        self.__fake_temperature = fake_temperature
        self.__fake_pressure = fake_pressure
        self.__fake_humidity = fake_humidity

    @override
    def get_environment_data(self) -> EnvironmentData:
        return EnvironmentData(
            self.__fake_temperature + random.randint(-25, 25) / 100,
            self.__fake_pressure + random.randint(-25, 25) / 100,
            self.__fake_humidity + random.randint(-25, 25) / 10000
        )

    @override
    def get_device_status(self) -> ConnectionStatus:
        return ConnectionStatus.CONNECTED
