from abc import ABC, abstractmethod
from typing import Tuple
from PIL import Image


class BaseInterface(ABC):

    @property
    @abstractmethod
    def resolution(self) -> Tuple[int, int]:
        raise NotImplementedError

    def show(self, image: Image):
        raise NotImplementedError
