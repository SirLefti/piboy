from abc import ABC, abstractmethod
from PIL import ImageDraw


class BaseApp(ABC):

    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def draw(self, draw: ImageDraw) -> ImageDraw:
        raise NotImplementedError
