import io
import logging
import threading
import time
from typing import Union

import pynmea2
import serial
from pynmea2 import GLL

from core.data import DeviceStatus
from core.decorator import override
from data.LocationProvider import Location, LocationException, LocationProvider

logger = logging.getLogger('location_data')

class SerialGPSLocationProvider(LocationProvider):

    def __init__(self, port: str, baud_rate=9600):
        self.__device = serial.Serial(port, baudrate=baud_rate, timeout=0.5)
        self.__io_wrapper = io.TextIOWrapper(io.BufferedReader(self.__device))
        self.__location: Union[Location, None] = None
        self.__device_status = DeviceStatus.UNAVAILABLE
        self.__thread = threading.Thread(target=self.__update_location, args=(), daemon=True)
        self.__thread.start()

    def __update_location(self):
        while True:
            try:
                data = self.__io_wrapper.readline()
                if len(data) == 0:
                    self.__device_status = DeviceStatus.UNAVAILABLE
                    continue
                logger.debug(data.strip())
                if data[0:6] == '$GPGLL':
                    message: GLL = pynmea2.parse(data)
                    # lat and lon are strings that are empty if the connection is lost
                    if message.lat != '' and message.lon != '':
                        self.__device_status = DeviceStatus.OPERATIONAL
                        self.__location = Location(message.latitude, message.longitude)
                    else:
                        self.__device_status = DeviceStatus.NO_DATA
                        self.__location = None
            except serial.SerialException as e:
                # connection issues: wait before trying again to avoid cpu load if the problem persists
                logger.warning(e)
                self.__device_status = DeviceStatus.UNAVAILABLE
                time.sleep(5)
            except pynmea2.ParseError as e:
                logger.warning(e)
            except UnicodeDecodeError as e:
                logger.warning(e)

    @override
    def get_location(self) -> Location:
        if self.__location is None:
            raise LocationException('GPS module has currently no signal')
        return self.__location

    @override
    def get_device_status(self) -> DeviceStatus:
        return self.__device_status
