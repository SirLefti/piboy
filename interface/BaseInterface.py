from abc import ABC, abstractmethod
from PIL import Image


class BaseInterface(ABC):

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @abstractmethod
    def show(self, image: Image):
        raise NotImplementedError
