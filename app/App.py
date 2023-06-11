from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from PIL import Image
import threading
import time


class App(ABC):
    """Basic app implementation."""

    @property
    @abstractmethod
    def title(self) -> str:
        """Title of the app shown in the header. Use ideally three or four capital letters."""
        raise NotImplementedError

    @abstractmethod
    def draw(self, image: Image, partial=False) -> (Image, int, int):
        """
        Draws the app content and returns the full or partial frame.

        Parameter image is the previous frame to draw on.
        Parameter partial indicates, if a full or partial frame was requested.
        It is not required to return a partial frame when requested, but highly recommended to always return a full
        when requested to make sure old frame parts are replaced.

        Returns a tuple of (image, int, int), which is the new frame and the x and y anchor relative to the top left
        corner. For a full frame, the coordinates have to be both 0. A partial frame has to be cropped accordingly.
        """
        raise NotImplementedError

    @abstractmethod
    def on_key_left(self):
        """Called when the 'left' key is pressed. Apps can change their state if they want for the next draw call."""
        raise NotImplementedError

    @abstractmethod
    def on_key_right(self):
        """Called when the 'right' key is pressed. Apps can change their state if they want for the next draw call."""
        raise NotImplementedError

    @abstractmethod
    def on_key_up(self):
        """Called when the 'up' key is pressed. Apps can change their state if they want for the next draw call."""
        raise NotImplementedError

    @abstractmethod
    def on_key_down(self):
        """Called when the 'down' key is pressed. Apps can change their state if they want for the next draw call."""
        raise NotImplementedError

    @abstractmethod
    def on_key_a(self):
        """Called when the 'a' key is pressed. Apps can change their state if they want for the next draw call."""
        raise NotImplementedError

    @abstractmethod
    def on_key_b(self):
        """Called when the 'b' key is pressed. Apps can change their state if they want for the next draw call."""
        raise NotImplementedError

    @abstractmethod
    def on_app_enter(self):
        """Called when entering the app. Apps can perform initial actions here."""
        raise NotImplementedError

    @abstractmethod
    def on_app_leave(self):
        """Called when leaving the app. Apps can perform cleanup actions here."""
        raise NotImplementedError


class SelfUpdatingApp(App, ABC):
    """App template, that can update itself at a fixed refresh time."""

    class UpdateThread:
        """Wrapper for an update thread, that keeps an eye on the time difference."""

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
            """Starts the inner thread function."""
            self.__alive = True
            self.__thread = threading.Thread(target=self.__thread_function, args=(), daemon=True)
            self.__thread.start()

        def stop(self):
            """Stops the inner thread function by setting a flag."""
            self.__alive = False

    def __init__(self, update_callback: Callable[[Any], None]):
        self.__update_callback = update_callback
        self.__update_thread: Optional[SelfUpdatingApp.UpdateThread] = None

    @property
    @abstractmethod
    def refresh_time(self) -> float:
        """Time in seconds between self refreshed updates."""
        raise NotImplementedError

    def on_app_enter(self):
        self.start_updating()

    def on_app_leave(self):
        self.stop_updating()

    def start_updating(self):
        """Creates a new update thread wrapper and starts it."""
        self.__update_thread = self.UpdateThread(callback=self.__update_callback, sleep_time=self.refresh_time)
        self.__update_thread.start()

    def stop_updating(self):
        """Stops the update thread wrapper"""
        self.__update_thread.stop()
