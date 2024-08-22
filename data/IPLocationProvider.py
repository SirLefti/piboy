from core.decorator import override
from data.LocationProvider import LocationProvider, LocationException,  Location
from typing import Callable, Type, Collection
import time
import requests
import json
import random


def retry(exceptions: Collection[Type[Exception]], delay: float = 0, tries: int = -1):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            t = tries
            while t:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    t -= 1
                    if not t:
                        raise LocationException(f'Max retry {tries} reached, {func.__name__} failed', e)
                    time.sleep(delay)
        return wrapper
    return decorator


class IPLocationProvider(LocationProvider):

    def __init__(self, apply_inaccuracy: bool = False):
        """Creates a location provider using the public IP. Set 'apply_inaccuracy' to 'True' to add a random variation
        to the returned values to emulate a real GPS device."""
        self.__apply_inaccuracy = apply_inaccuracy

    @retry(exceptions=(requests.exceptions.ConnectionError,), delay=2, tries=5)
    @override
    def get_location(self) -> Location:
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
