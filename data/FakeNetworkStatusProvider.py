from core.data import DeviceStatus
from core.decorator import override
from data.NetworkStatusProvider import NetworkStatusProvider


class FakeNetworkStatusProvider(NetworkStatusProvider):

    @override
    def get_status(self) -> DeviceStatus:
        return DeviceStatus.OPERATIONAL
