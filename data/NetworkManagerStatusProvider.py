import subprocess
import time
from multiprocessing import Process

from core.decorator import override
from data.NetworkStatusProvider import NetworkStatus, NetworkStatusProvider


class NetworkManagerStatusProvider(NetworkStatusProvider):
    """Data provider for the network status using debians network-manager."""

    __status = NetworkStatus.DISCONNECTED

    def __init__(self):
        self.__process = Process(target=self.__update_status, args=(), daemon=True, name='network-status-update')
        self.__process.start()

    def __update_status(self):
        while True:
            result = subprocess.run(['nmcli', 'networking', 'connectivity'], capture_output=True, text=True)
            if 'full' in result.stdout:
                self.__status = NetworkStatus.CONNECTED
            else:
                self.__status = NetworkStatus.DISCONNECTED
            time.sleep(10)

    @override
    def get_status(self) -> NetworkStatus:
        return self.__status
