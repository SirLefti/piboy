import sys


try:
    if sys.version_info >= (3, 12):
        # override is available since python 3.12 out of the box
        from typing import override
    else:
        # in previous versions we can install typing-extensions
        from typing_extensions import override
except ImportError:
    # if the package is not installed, define a mock, because it is just needed for type checking
    import typing
    _F = typing.TypeVar("_F", bound=typing.Callable[..., typing.Any])
    def override(_: _F, /) -> _F: return _
