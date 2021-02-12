"""Test some simple combinations of functions and handlers."""
from unittest.mock import MagicMock

import pytest

import snake.shifter.wrapper
from snake.shifter import Context


decorators = [snake.shifter.wrapper.node]


@pytest.mark.parametrize("decorator", decorators)
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


@pytest.mark.parametrize("decorator", decorators)
def test_simple_failing_func(decorator):
    """Check we can construct a key, and cache in a dict."""
    # store a ref to the thrown exception outside the function
    # so we can check it's the same one returned
    exception = None

    @decorator
    def f(a, b):
        nonlocal exception
        # this exception should be cached by the wrapper
        # so we only see it once
        exception = RuntimeError("failure")

        raise exception

    with Context(dict()) as d:
        try:
            f(1, 2)
        except RuntimeError as e:
            assert e is exception

        with pytest.raises(RuntimeError):
            f(1, 2)

    assert type(d[f.key(1, 2)]) is Exception
    assert d[f.key(1, 2)].args[0] is exception


@pytest.mark.parametrize("decorator", decorators)
def test_mock_null_handler(decorator):
    """Check that a null mock handler is called correctly."""
    handler = MagicMock()
    handler.__contains__.return_value = False
    handler.__getitem__.return_value = None
    handler.__setitem__.return_value = None

    @decorator
    def f(a, b):
        return a + b

    with Context(handler):
        assert f(1, 2) == 3

    handler.__contains__.assert_called_once_with(f.key(1, 2))
    handler.__getitem__.assert_not_called()
    handler.__setitem__.assert_called_once_with(f.key(1, 2), 3)


@pytest.mark.parametrize("decorator", decorators)
def test_mock_cached_handler(decorator):
    """Check that a fixed value mock handler is called correctly."""
    handler = MagicMock()
    handler.__contains__.return_value = True
    handler.__getitem__.return_value = Ellipsis
    handler.__setitem__.return_value = None

    @decorator
    def f(a, b):
        raise AssertionError("this functino should not be called")

    with pytest.raises(AssertionError):
        f(1, 2)

    with Context(handler):
        assert f(1, 2) is Ellipsis

    print(handler.__getitem__.mock_calls)

    handler.__contains__.assert_called_once_with(f.key(1, 2))
    handler.__getitem__.assert_called_once_with(f.key(1, 2))
    handler.__setitem__.assert_not_called()
