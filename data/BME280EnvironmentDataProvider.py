import bme280
import smbus2

from core.decorator import override
from data.EnvironmentDataProvider import EnvironmentData, EnvironmentDataProvider


class BME280EnvironmentDataProvider(EnvironmentDataProvider):

    def __init__(self, port: int, address: int):
        self.__bus = smbus2.SMBus(port)
        self.__address = address

    @override
    def get_environment_data(self) -> EnvironmentData:
        data = bme280.sample(self.__bus, self.__address)
        return EnvironmentData(
            data.temperature,
            data.pressure,
            data.humidity / 100
        )
