import sys
import time
from typing import Any, Callable, Optional, Type, TypeVar

try:
    if sys.version_info >= (3, 12):
        # override is available since python 3.12 out of the box
        from typing import override
    else:
        # in previous versions we can install typing-extensions
        from typing_extensions import override
except ImportError:
    # if the package is not installed, define a mock, because it is just needed for type checking
    _F = TypeVar("_F", bound=Callable[..., Any])
    def override(_: _F, /) -> _F: return _


class RetryException(Exception):

    def __init__(self, message: str, inner_exception: Optional[Exception] = None):
        self.message = message
        self.inner_exception = inner_exception


def retry(exceptions: tuple[Type[Exception]], delay: float = 0, tries: int = -1):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            t = tries
            while t:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    t -= 1
                    if not t:
                        raise RetryException(f'Max retry {tries} reached, {func.__name__} failed', e)
                    time.sleep(delay)
        return wrapper
    return decorator
