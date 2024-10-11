from core.data import ConnectionStatus
from core.decorator import override
from data.NetworkStatusProvider import NetworkStatusProvider


class FakeNetworkStatusProvider(NetworkStatusProvider):

    def __init__(self, default_status = ConnectionStatus.DISCONNECTED):
        self.__default_status = default_status

    @override
    def get_status(self) -> ConnectionStatus:
        return self.__default_status
