"""Implementation of call tracker using a function wrapper via a decorator.

This a refernce implementation to make it clear how the
handler interacts with the function and to provide a
benchmark implementation to test the other approaches against.
"""
import functools
import inspect
from collections import namedtuple


def node(func):
    """Wrap a function with calls to a handler to modify it's behaviour.

    Args:
        func: the function to modify

    Returns:
        the modified function
    """
    sig = inspect.signature(func)

    key_type = namedtuple(
        func.__name__,
        sig.parameters.keys(),
        module=func.__module__,
    )
    key_type.func = func

    # patch the repr so we display the full function name
    repr_fmt = "(" + ", ".join(f"{name}=%r" for name in sig.parameters.keys()) + ")"

    def _repr(self):
        return self.__module__ + "." + self.__class__.__name__ + repr_fmt % self

    key_type.__repr__ = _repr

    # import the global context handler stack here, which we bind into the wrapper
    from .context import _handlers

    @functools.wraps(func)
    def _func(*args, **kwargs):
        handler = _handlers[-1]

        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        key = key_type._make(bound.args)

        if key in handler:
            value = handler[key]
            if type(value) is Exception:
                raise value.args[0] from value.args[0]

            return handler[key]
        try:
            retval = func(*args, **kwargs)
            handler[key] = retval
            return retval
        except Exception as exc:
            handler[key] = Exception(exc)
            raise

    _func.key = key_type
    return _func
