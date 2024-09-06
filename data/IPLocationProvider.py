from core.decorator import override, retry, RetryException
from data.LocationProvider import LocationProvider, LocationException, Location, LocationStatus
import requests
import json
import random


class IPLocationProvider(LocationProvider):

    def __init__(self, apply_inaccuracy: bool = False):
        """Creates a location provider using the public IP. Set 'apply_inaccuracy' to 'True' to add a random variation
        to the returned values to emulate a real GPS device."""
        self.__apply_inaccuracy = apply_inaccuracy
        self.__status = LocationStatus.DISCONNECTED

    @retry(exceptions=(requests.exceptions.ConnectionError,), delay=2, tries=5)
    def __fetch_location(self) -> Location:
        response = requests.get('https://ipinfo.io/json')
        if response.status_code != 200:
            raise LocationException(f'Fetching coordinates by IP failed ({response.status_code})')

        data = json.loads(response.content)
        loc = 'loc'
        if loc not in data.keys():
            raise LocationException(f'Response data does not contain key ({loc})')

        values = str.split(data[loc], ',')
        if len(values) != 2:
            raise LocationException('Response data does not contain two coordinates')

        if self.__apply_inaccuracy:
            lat_offset = random.randint(-100, 100)
            lon_offset = random.randint(-100, 100)
            return Location(float(values[0]) + lat_offset / 1000000,
                            float(values[1]) + lon_offset / 10000000)
        else:
            return Location(float(values[0]), float(values[1]))

    @override
    def get_location(self) -> Location:
        try:
            location = self.__fetch_location()
            self.__status = LocationStatus.CONNECTED
            return location
        except RetryException:
            self.__status = LocationStatus.DISCONNECTED
            raise LocationException('Fetching location failed')

    @override
    def get_status(self) -> LocationStatus:
        return self.__status
