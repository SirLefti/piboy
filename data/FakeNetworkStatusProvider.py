from core.data import ConnectionStatus
from core.decorator import override
from data.NetworkStatusProvider import NetworkStatusProvider


class FakeNetworkStatusProvider(NetworkStatusProvider):

    @override
    def get_connection_status(self) -> ConnectionStatus:
        return ConnectionStatus.CONNECTED
