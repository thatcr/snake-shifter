"""Test some simple combinations of functions and handlers."""
import pytest

import snake.shifter.wrapper
from snake.shifter import Context


@pytest.mark.parametrize("decorator", [snake.shifter.wrapper.node])
def test_simple_func(decorator):
    """Check we can construct a key, and cache in a dict."""

    @decorator
    def f(a, b):
        return a + b

    assert repr(f.key(1, 2)) == f"{__name__}.f(a=1, b=2)"

    with Context(dict()) as d:
        f(1, 2)
        f(1, 2)

    assert d[f.key(1, 2)] == 3


@pytest.mark.parametrize("decorator", [snake.shifter.wrapper.node])
def test_simple_failing_func(decorator):
    """Check we can construct a key, and cache in a dict."""
    exception = None

    @decorator
    def f(a, b):
        nonlocal exception
        if exception is None:
            exception = RuntimeError("failure")

        raise exception

    with Context(dict()) as d:
        try:
            f(1, 2)
        except RuntimeError:
            pass

        with pytest.raises(RuntimeError):
            f(1, 2)

    assert type(d[f.key(1, 2)]) is Exception
    assert d[f.key(1, 2)].args[0] is exception
