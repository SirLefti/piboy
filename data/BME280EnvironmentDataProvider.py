import bme280
import smbus2

from core.data import ConnectionStatus
from core.decorator import override
from data.EnvironmentDataProvider import EnvironmentData, EnvironmentDataProvider


class BME280EnvironmentDataProvider(EnvironmentDataProvider):

    def __init__(self, port: int, address: int):
        self.__bus = smbus2.SMBus(port)
        self.__address = address
        self.__device_status = ConnectionStatus.DISCONNECTED

    @override
    def get_environment_data(self) -> EnvironmentData:
        try:
            data = bme280.sample(self.__bus, self.__address)
            self.__device_status = ConnectionStatus.CONNECTED
            return EnvironmentData(
                data.temperature,
                data.pressure,
                data.humidity / 100
            )
        except OSError as e:
            self.__device_status = ConnectionStatus.DISCONNECTED
            raise e

    @override
    def get_device_status(self) -> ConnectionStatus:
        return self.__device_status
