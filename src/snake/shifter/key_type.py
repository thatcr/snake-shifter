"""Build a type to represent a function signature."""
import inspect
from collections import namedtuple
from typing import Any
from typing import Callable

from .typing import CallKey


def make_key_type(func: Callable[..., Any]) -> Callable[..., CallKey]:
    """Construct a type representing a functions signature."""
    sig = inspect.signature(func)

    # patch the repr so we display the full function name
    repr_fmt = "(" + ", ".join(f"{name}=%r" for name in sig.parameters.keys()) + ")"

    def _repr(self: Any) -> Any:
        return self.__module__ + "." + self.__class__.__name__ + repr_fmt % self[:-1]

    key_type = type(
        func.__name__,
        (
            namedtuple(
                func.__name__,
                tuple(sig.parameters.keys()) + ("func__",),
                defaults=tuple(p.default for p in sig.parameters.values()) + (func,),
                module=func.__module__,
            ),
            CallKey,
        ),
        {
            "__repr__": _repr,
            "__func__": func,
            "__module__": func.__module__,
            "__signature__": sig,
        },
    )

    return key_type
