from core.data import ConnectionStatus
from core.decorator import override
from data.BatteryStatusProvider import BatteryStatusProvider


class FakeBatteryStatusProvider(BatteryStatusProvider):
    @override
    def get_state_of_charge(self) -> float:
        return 1.0

    @override
    def get_device_status(self) -> ConnectionStatus:
        return ConnectionStatus.CONNECTED
