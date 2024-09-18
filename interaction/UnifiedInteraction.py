from abc import ABC

from interaction.Display import Display
from interaction.Input import Input


class UnifiedInteraction(Input, Display, ABC):
    pass
