"""Base classes for core abstractions, typing."""
from typing import Any
from typing import Callable
from typing import Tuple
from typing import TypeVar

from typing_extensions import Protocol


class CallKey(Tuple[Any, ...]):
    """A call key refers to a function call and is a tuple of it's arguments."""

    pass


class CallHandler(Protocol):
    """Handler invoked from node functions when they are called."""

    def __contains__(self, key: CallKey) -> bool:
        """Check to see if we should execute the current call."""
        ...

    def __setitem__(self, key: CallKey, value: Any) -> None:
        """When executed set the returned value for the call."""
        ...

    def __getitem__(self, key: CallKey) -> Any:
        """Otherwise retrieve the value that should be returned."""
        ...


F = TypeVar("F", bound=Callable[..., Any])


class Decorator(Protocol):
    """Protocol for transforming a function to a shifted function."""

    def __call__(self, func: F) -> F:
        """Process the supplied function so it can be shifted."""
        ...
