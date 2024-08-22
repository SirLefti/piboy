from core.decorator import override
from data.LocationProvider import LocationProvider, LocationException, Location
from typing import Union
import serial
import io
import pynmea2
import threading


class SerialGPSLocationProvider(LocationProvider):

    def __init__(self, port: str, baudrate=9600):
        self.__device = serial.Serial(port, baudrate=baudrate, timeout=0.5)
        io.BufferedReader(self.__device)
        self.__io_wrapper = io.TextIOWrapper(io.BufferedRWPair(self.__device, self.__device))
        self.__location: Union[Location, None] = None
        self.__thread = threading.Thread(target=self.__update_location, args=(), daemon=True)
        self.__thread.start()

    def __update_location(self):
        while 1:
            try:
                data = self.__io_wrapper.readline()
                if data[0:6] == '$GPRMC':
                    message = pynmea2.parse(data)
                    # lat and lon are strings that are empty if the connection is lost
                    if message.lat != '' and message.lon != '':
                        self.__location = Location(message.latitude, message.longitude)
                    else:
                        self.__location = None
            except serial.SerialException:
                pass
            except pynmea2.ParseError:
                pass

    @override
    def get_location(self) -> Location:
        if self.__location is None:
            raise LocationException('GPS module has currently no signal')
        return self.__location
