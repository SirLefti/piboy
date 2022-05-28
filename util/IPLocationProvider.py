from util.BaseLocationProvider import BaseLocationProvider
from typing import Tuple
import requests
import json


class IPLocationProvider(BaseLocationProvider):

    def get_location(self) -> Tuple[float, float]:
        response = requests.get('https://ipinfo.io/json')
        if response.status_code == 200:
            data = json.loads(response.content)
            loc = 'loc'
            if loc in data.keys():
                values = str.split(data[loc], ',')
                if len(values) == 2:
                    return float(values[0]), float(values[1])
                else:
                    raise ValueError('Response data does not contain two coordinates')
            else:
                raise ValueError(f'Response data does not contain key ({loc})')
        else:
            raise ValueError(f'Fetching coordinates by IP failed ({response.status_code})')
