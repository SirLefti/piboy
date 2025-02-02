import bme280
import smbus2

from core.data import DeviceStatus
from core.decorator import override
from data.EnvironmentDataProvider import EnvironmentData, EnvironmentDataProvider


class BME280EnvironmentDataProvider(EnvironmentDataProvider):

    def __init__(self, port: int, address: int):
        self.__bus = smbus2.SMBus(port)
        self.__address = address
        self.__device_status = DeviceStatus.UNAVAILABLE

    @override
    def get_environment_data(self) -> EnvironmentData:
        try:
            data = bme280.sample(self.__bus, self.__address)
            self.__device_status = DeviceStatus.OPERATIONAL
            return EnvironmentData(
                data.temperature,
                data.pressure,
                data.humidity / 100
            )
        except OSError as e:
            self.__device_status = DeviceStatus.UNAVAILABLE
            raise e

    @override
    def get_device_status(self) -> DeviceStatus:
        return self.__device_status
