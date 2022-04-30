from abc import ABC, abstractmethod
from PIL import Image


class BaseApp(ABC):

    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def draw(self, image: Image) -> Image:
        raise NotImplementedError
