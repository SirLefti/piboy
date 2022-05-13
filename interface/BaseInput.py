from abc import ABC, abstractmethod


class BaseInput(ABC):

    @abstractmethod
    def on_key_left(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_up(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_right(self):
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

    @abstractmethod
    def on_rotary_increase(self):
        raise NotImplementedError

    @abstractmethod
    def on_rotary_decrease(self):
        raise NotImplementedError
