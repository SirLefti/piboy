from enum import Enum


class DeviceStatus(Enum):
    OPERATIONAL = 1,
    NO_DATA = 2,
    UNAVAILABLE = 3


class ConnectionStatus(Enum):
    CONNECTED = 1,
    DISCONNECTED = 2
