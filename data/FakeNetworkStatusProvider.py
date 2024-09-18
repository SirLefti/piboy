from core.decorator import override
from data.NetworkStatusProvider import NetworkStatus, NetworkStatusProvider


class FakeNetworkStatusProvider(NetworkStatusProvider):

    def __init__(self, default_status = NetworkStatus.DISCONNECTED):
        self.__default_status = default_status

    @override
    def get_status(self) -> NetworkStatus:
        return self.__default_status
