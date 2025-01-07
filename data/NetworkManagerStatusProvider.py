import subprocess
import threading
import time

from core.data import DeviceStatus
from core.decorator import override
from data.NetworkStatusProvider import NetworkStatusProvider


class NetworkManagerStatusProvider(NetworkStatusProvider):
    """Data provider for the network status using debians network-manager."""

    __status = DeviceStatus.NO_DATA

    def __init__(self):
        self.__thread = threading.Thread(target=self.__update_status, args=(), daemon=True)
        self.__thread.start()

    def __update_status(self):
        while True:
            result = subprocess.run(['nmcli', 'networking', 'connectivity'], capture_output=True, text=True)
            if 'full' in result.stdout:
                self.__status = DeviceStatus.OPERATIONAL
            else:
                self.__status = DeviceStatus.NO_DATA
            time.sleep(10)

    @override
    def get_status(self) -> DeviceStatus:
        return self.__status
