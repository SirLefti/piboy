from EnvironmentDataProvider import EnvironmentDataProvider, EnvironmentData
import bme280
import smbus2


class BME280EnvironmentDataProvider(EnvironmentDataProvider):

    def __init__(self, port: int, address: int):
        self.__bus = smbus2.SMBus(port)
        self.__address = address

    def get_environment_data(self) -> EnvironmentData:
        data = bme280.sample(self.__bus, self.__address)
        return EnvironmentData(
            data.temperature,
            data.pressure,
            data.humidity
        )
