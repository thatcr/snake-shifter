"""Snake Shifter."""
from typing import Any
from typing import Callable

from .context import CallHandler
from .context import CallKey
from .context import Context


def key(func: Callable[..., Any], *args: Any, **kwargs: Any) -> CallKey:
    """Construct a key to a function call with the given arguments."""
    # since we are preserving fundamental python types as far as possible
    # we disable type checking here, __key__ is an implementation detail.
    return func.__key__(*args, **kwargs)  # type: ignore


class CallableDecorator:
    """Type definition for function transformation decorator."""

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Convert a regular Callable definition to a shifted one."""
        pass


__all__ = ["Context", "key", "CallHandler", "CallKey", "CallableDecorator"]
