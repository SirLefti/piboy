from abc import ABC
from interaction.Input import Input
from interaction.Display import Display


class UnifiedInteraction(Input, Display, ABC):
    pass
