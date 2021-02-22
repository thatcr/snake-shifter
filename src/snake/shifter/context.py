"""Context manager and empty handler."""
from abc import ABCMeta
from abc import abstractmethod
from types import TracebackType
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type


class CallKey(Tuple[Any, ...]):
    """A call key refers to a function call and is a tupleof it's arguments."""

    pass


class CallHandler(metaclass=ABCMeta):
    """Handler invoked from node functions when they are called."""

    @abstractmethod
    def __contains__(self, key: CallKey) -> bool:
        """Test to see if this call should be handled by the __getitem__."""
        return False

    @abstractmethod
    def __getitem__(self, key: CallKey) -> Any:
        """Return the value to return for a call."""
        return NotImplemented

    @abstractmethod
    def __setitem__(self, key: CallKey, value: Any) -> None:
        """Receive the value calculated for a call."""
        return None


class NullHandler(CallHandler):
    """Handler that does nothing."""

    def __contains__(self, key: CallKey) -> bool:
        """Avoid handling anything."""
        return False

    def __getitem__(self, key: CallKey) -> Any:
        """We never cache any values on this handler."""
        raise NotImplementedError()

    def __setitem__(self, key: CallKey, value: Any) -> None:
        """Never process any function results."""
        pass


class Context(object):
    """Context handler that maintains a stack of handlers."""

    # global stack of handlers, tail element is used for t
    # the active handler.
    # TODO make this thread/coroutine safe
    _handlers: List[CallHandler] = [NullHandler()]

    def __init__(self, handler: CallHandler):
        """Initialize context with a handler instance."""
        self.handler = handler

    def __enter__(self) -> CallHandler:
        """Push the handler onto the global stack."""
        global _handlers
        Context._handlers.append(self.handler)
        return self.handler

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Remove handler from the global stack."""
        Context._handlers.pop(-1)
        return True


def get_handler() -> CallHandler:
    """Return the active handler at the top of the stack."""
    return Context._handlers[-1]
