from abc import ABC, abstractmethod
from typing import Optional, Callable, Any

from PIL import Image
import threading
import time


class App(ABC):

    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def draw(self, image: Image, partial=False) -> (Image, int, int):
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

    @abstractmethod
    def on_app_enter(self):
        raise NotImplementedError

    @abstractmethod
    def on_app_leave(self):
        raise NotImplementedError


class SelfUpdatingApp(App, ABC):

    class UpdateThread:

        def __init__(self, callback: Callable[[], None], sleep_time: float):
            self.__callback = callback
            self.__sleep_time = sleep_time
            self.__thread: Optional[threading.Thread] = None
            self.__alive = False

        def __thread_function(self):
            next_call = time.time()
            while self.__alive:
                self.__callback()
                next_call = next_call + self.__sleep_time
                diff = max(next_call - time.time(), 0)  # make sure it is not negative
                time.sleep(diff)

        def start(self):
            self.__alive = True
            self.__thread = threading.Thread(target=self.__thread_function, args=(), daemon=True)
            self.__thread.start()

        def stop(self):
            self.__alive = False

    def __init__(self, update_callback: Callable[[Any], None]):
        self.__update_callback = update_callback
        self.__update_thread: Optional[SelfUpdatingApp.UpdateThread] = None

    @property
    @abstractmethod
    def refresh_time(self) -> float:
        raise NotImplementedError

    def on_app_enter(self):
        self.start_updating()

    def on_app_leave(self):
        self.stop_updating()

    def start_updating(self):
        self.__update_thread = self.UpdateThread(callback=self.__update_callback, sleep_time=self.refresh_time)
        self.__update_thread.start()

    def stop_updating(self):
        self.__update_thread.stop()
