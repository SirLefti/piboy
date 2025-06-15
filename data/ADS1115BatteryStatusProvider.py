import logging
import time
from collections import deque

import smbus2

from core.data import DeviceStatus
from core.decorator import override
from data.BatteryStatusProvider import BatteryStatusProvider

logger = logging.getLogger('battery_data')

class ADS1115BatteryStatusProvider(BatteryStatusProvider):

    __CONVERSION_REG = 0x00
    __CONFIG_REG = 0x01

    __FSR = 6.144 # full scale range

    __V_CHARGED = 4.2
    __V_DISCHARGED = 2.9

    __last_levels = deque(maxlen=10)

    def __init__(self, port: int, address: int):
        self.__bus = smbus2.SMBus(port)
        self.__address = address
        self.__device_status = DeviceStatus.UNAVAILABLE

    def __read_channel(self, channel=0) -> float:
        config = [
            0b11000001 | (channel << 4), # GND as reference, select channel
            0b10000011                   # default settings
        ]
        self.__bus.write_i2c_block_data(self.__address, self.__CONFIG_REG, config)
        time.sleep(0.1)
        word_data = self.__bus.read_word_data(self.__address, self.__CONVERSION_REG)
        self.__device_status = DeviceStatus.OPERATIONAL
        # swap bytes in word
        raw_data = ((word_data & 0xFF) << 8) | (word_data >> 8)
        logger.debug(f'{raw_data=}')
        # 0x000 - 0x7FFF -> 0 ... +FSR | 0x8000 - 0xFFFF -> -FSR ... 0
        return (raw_data if raw_data < 0x8000 else raw_data - 0x10000) * self.__FSR / 0x8000

    @override
    def get_state_of_charge(self) -> float:
        try:
            voltage = self.__read_channel()
            logger.debug(f'{voltage=}')
            if voltage < 1.5:
                self.__device_status = DeviceStatus.NO_DATA
                return 0.0
            else:
                self.__last_levels.append(voltage)
                smoothed_voltage = sum(self.__last_levels) / len(self.__last_levels)
                if smoothed_voltage < self.__V_DISCHARGED:
                    return 0
                elif smoothed_voltage > self.__V_CHARGED:
                    return 1
                else:
                    return (smoothed_voltage - self.__V_DISCHARGED) / (self.__V_CHARGED - self.__V_DISCHARGED)
        except OSError as e:
            logger.warning(e)
            self.__device_status = DeviceStatus.UNAVAILABLE
            return 0.0


    @override
    def get_device_status(self) -> DeviceStatus:
        return self.__device_status
