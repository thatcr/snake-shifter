"""Base classes for core abstractions, typing."""
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Tuple
from typing import TypeVar

from typing_extensions import Protocol


class CallKey(Tuple[Any, ...]):
    """A call key refers to a function call and is a tupleof it's arguments."""

    pass  # pragma: no cover


class CallHandler(metaclass=ABCMeta):
    """Handler invoked from node functions when they are called."""

    @abstractmethod
    def __contains__(self, key: CallKey) -> bool:
        """Test to see if this call should be handled by the __getitem__."""
        return False  # pragma: no cover

    @abstractmethod
    def __getitem__(self, key: CallKey) -> Any:
        """Return the value to return for a call."""
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key: CallKey, value: Any) -> None:
        """Receive the value calculated for a call."""
        return None  # pragma: no cover


F = TypeVar("F", bound=Callable[..., Any])


class Decorator(Protocol):
    """Protocol for transforming a function to a shifted function."""

    def __call__(self, func: F) -> F:
        """Shift the function."""
        pass
