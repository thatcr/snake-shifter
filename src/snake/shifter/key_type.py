"""Build a type to represent a function signature."""
import inspect
from collections import namedtuple
from typing import Any
from typing import Callable
from typing import cast

from .typing import CallKey


def make_key_type(func: Callable[..., Any]) -> Callable[..., CallKey]:
    """Construct a type representing a functions signature."""
    sig = inspect.signature(func)

    # patch the repr so we display the full function name
    repr_fmt = (
        (
            func.__name__
            if "<locals>" in func.__qualname__
            else func.__module__ + "." + func.__qualname__
        )
        + "("
        + ", ".join(name + "={!r}" for name in sig.parameters.keys())
        + ")"
    )

    def _repr(self: Any) -> str:
        return cast(str, repr_fmt.format(*self[:-1]))

    # build the tuple from a call signature - note we can't use
    # the new/init from the named tuple as it won't unpack the
    # same way as the function call.
    @classmethod
    def from_call(cls: Any, *args: Any, **kwargs: Any):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # this is wrong - how do we yunpack exactly the right args to mach
        # the list in the tuple?

        return key_type(*bound.arguments.values())

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
            "from_call": from_call,
        },
    )

    return key_type
