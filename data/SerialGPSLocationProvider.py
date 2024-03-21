from data.LocationProvider import LocationProvider, LocationException
from typing import Union
import serial
import io
import pynmea2
import threading

class SerialGPSLocationProvider(LocationProvider):

    def __init__(self, port: str, baudrate=9600):
        self.__device = serial.Serial(port, baudrate=baudrate, timeout=0.5)
        self.__io_wrapper = io.TextIOWrapper(io.BufferedRWPair(self.__device, self.__device))
        self.__lat: Union[float, None] = None
        self.__lon: Union[float, None] = None
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
                        self.__lat = message.latitude
                        self.__lon = message.longitude
                    else:
                        self.__lat = None
                        self.__lon = None
            except serial.SerialException:
                pass
            except pynmea2.ParseError:
                pass

    def get_location(self) -> tuple[float, float]:
        if self.__lat is None or self.__lon is None:
            raise LocationException('GPS module has currently no signal')
        return self.__lat, self.__lon

