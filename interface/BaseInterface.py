from abc import ABC, abstractmethod
from PIL import Image


class BaseInterface(ABC):

    @property
    @abstractmethod
    def resolution(self) -> tuple:
        raise NotImplementedError

    def show(self, image: Image):
        raise NotImplementedError
