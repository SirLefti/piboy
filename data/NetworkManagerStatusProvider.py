from data.NetworkStatusProvider import NetworkStatusProvider, NetworkStatus
from core.decorator import override
import subprocess
import threading
import time


class NetworkManagerStatusProvider(NetworkStatusProvider):
    """Data provider for the network status using debians network-manager."""

    __status = NetworkStatus.DISCONNECTED

    def __init__(self):
        self.__thread = threading.Thread(target=self.__update_status, args=(), daemon=True)
        self.__thread.start()

    def __update_status(self):
        while True:
            result = subprocess.run(['nmcli', 'networking', 'connectivity'], capture_output=True, text=True)
            if result.stdout == 'full':
                self.__status = NetworkStatus.CONNECTED
            else:
                self.__status = NetworkStatus.DISCONNECTED
            time.sleep(10)

    @override
    def get_status(self) -> NetworkStatus:
        return self.__status
