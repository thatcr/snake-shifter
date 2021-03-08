"""Snake Shifter."""
from typing import Any
from typing import Callable

from .context import Context
from .typing import CallKey
from .wrapper import shift


def key(func: Callable[..., Any], *args: Any, **kwargs: Any) -> CallKey:
    """Construct a key to a function call with the given arguments."""
    # since we are preserving fundamental python types as far as possible
    # we disable type checking here, __key__ is an implementation detail.
    return func.__key__.from_call(*args, **kwargs)  # type: ignore


__all__ = ["Context", "key", "shift"]
