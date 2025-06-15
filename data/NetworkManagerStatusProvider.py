import logging
import subprocess
import threading
import time

from core.data import ConnectionStatus
from core.decorator import override
from data.NetworkStatusProvider import NetworkStatusProvider

logger = logging.getLogger('network_data')

class NetworkManagerStatusProvider(NetworkStatusProvider):
    """Data provider for the network status using debians network-manager."""

    __status = ConnectionStatus.DISCONNECTED

    def __init__(self):
        self.__thread = threading.Thread(target=self.__update_status, args=(), daemon=True)
        self.__thread.start()

    def __update_status(self):
        while True:
            result = subprocess.run(['nmcli', 'networking', 'connectivity'], capture_output=True, text=True)
            if 'full' in result.stdout:
                self.__status = ConnectionStatus.CONNECTED
            else:
                self.__status = ConnectionStatus.DISCONNECTED
            logger.debug(result.stdout)
            time.sleep(10)

    @override
    def get_connection_status(self) -> ConnectionStatus:
        return self.__status
