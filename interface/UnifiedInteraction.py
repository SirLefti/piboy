from abc import ABC
from interface.Input import Input
from interface.Interface import Interface


class UnifiedInteraction(Input, Interface, ABC):
    pass
