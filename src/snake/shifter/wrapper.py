"""Implementation of call tracker using a function wrapper via a decorator.

This a reference implementation to make it clear how the
handler interacts with the function and to provide a
benchmark implementation to test the other approaches against.
"""
import functools
import inspect
from collections import namedtuple
from typing import Any
from typing import Callable
from typing import TypeVar

from .context import CallKey

T = TypeVar("T")


def node(func: Callable[..., T]) -> Callable[..., T]:
    """Wrap a function with calls to a handler to modify it's behaviour.

    Args:
        func: the function to modify

    Returns:
        the modified function
    """
    sig = inspect.signature(func)

    # patch the repr so we display the full function name
    repr_fmt = "(" + ", ".join(f"{name}=%r" for name in sig.parameters.keys()) + ")"

    def _repr(self: Any) -> Any:
        return self.__module__ + "." + self.__class__.__name__ + repr_fmt % self

    key_type = type(
        func.__name__,
        (
            namedtuple(
                func.__name__,
                sig.parameters.keys(),
                module=func.__module__,
            ),
            CallKey,
        ),
        {"__repr__": _repr, "__func__": func, "__module__": func.__module__},
    )

    # import the global context handler stack here, which we bind into the wrapper
    from .context import Context

    @functools.wraps(func)
    def _func(*args: Any, **kwargs: Any) -> Any:
        handler = Context._handlers[-1]

        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        key = key_type(*bound.args)

        if key in handler:
            value = handler[key]
            if type(value) is Exception:
                raise value.args[0] from value.args[0]

            return value
        try:
            retval = func(*args, **kwargs)
            handler[key] = retval
            return retval
        except Exception as exc:
            handler[key] = Exception(exc)
            raise

    _func.__key__ = key_type  # type: ignore
    return _func
