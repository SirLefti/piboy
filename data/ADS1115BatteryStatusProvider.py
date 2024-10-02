import smbus2

from core.decorator import override
from data.BatteryStatusProvider import BatteryStatusProvider


class ADS1115BatteryStatusProvider(BatteryStatusProvider):

    def __init__(self, port: int, address: int):
        self.__bus = smbus2.SMBus(port)
        self.__address = address

    @override
    def get_state_of_charge(self) -> float:
        return 1.0
