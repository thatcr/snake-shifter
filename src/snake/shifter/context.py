"""Context manager and empty handler."""
from types import TracebackType
from typing import Any
from typing import List
from typing import Optional
from typing import Type

from .typing import CallHandler
from .typing import CallKey


class NullHandler:
    """Handler that does nothing.

    Example:
        >>> handler = NullHandler()
        >>> 1 in handler
        False
    """

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

    def __exit__(  # type: ignore
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Remove handler from the global stack."""
        Context._handlers.pop(-1)
        return False


def get_handler() -> CallHandler:
    """Return the active handler at the top of the stack."""
    return Context._handlers[-1]
