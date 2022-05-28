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

    @abstractmethod
    def on_key_left(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_right(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_up(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_down(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_a(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_b(self):
        raise NotImplementedError
