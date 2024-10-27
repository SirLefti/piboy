import io
import threading
import time
from typing import Union

import pynmea2
import serial

from core.data import ConnectionStatus
from core.decorator import override
from data.LocationProvider import Location, LocationException, LocationProvider


class SerialGPSLocationProvider(LocationProvider):

    def __init__(self, port: str, baudrate=9600):
        self.__device = serial.Serial(port, baudrate=baudrate, timeout=0.5)
        io.BufferedReader(self.__device)
        self.__io_wrapper = io.TextIOWrapper(io.BufferedRWPair(self.__device, self.__device))
        self.__location: Union[Location, None] = None
        self.__device_status = ConnectionStatus.DISCONNECTED
        self.__thread = threading.Thread(target=self.__update_location, args=(), daemon=True)
        self.__thread.start()

    def __update_location(self):
        while True:
            try:
                data = self.__io_wrapper.readline()
                self.__device_status = ConnectionStatus.CONNECTED
                if data[0:6] == '$GPRMC':
                    message = pynmea2.parse(data)
                    # lat and lon are strings that are empty if the connection is lost
                    if message.lat != '' and message.lon != '':
                        self.__location = Location(message.latitude, message.longitude)
                    else:
                        self.__location = None
            except serial.SerialException:
                # connection issues: wait before trying again to avoid cpu load if the problem persists
                self.__device_status = ConnectionStatus.DISCONNECTED
                time.sleep(5)
            except pynmea2.ParseError:
                pass

    @override
    def get_location(self) -> Location:
        if self.__location is None:
            raise LocationException('GPS module has currently no signal')
        return self.__location

    @override
    def get_status(self) -> ConnectionStatus:
        if self.__location is None:
            return ConnectionStatus.DISCONNECTED
        else:
            return ConnectionStatus.CONNECTED

    @override
    def get_device_status(self) -> ConnectionStatus:
        return self.__device_status
