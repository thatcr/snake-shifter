"""Test some simple combinations of functions and handlers."""
from typing import Any
from unittest.mock import MagicMock

import pytest

import snake.shifter.wrapper
from snake.shifter import CallableDecorator
from snake.shifter import CallHandler
from snake.shifter import CallKey
from snake.shifter import Context
from snake.shifter import key


decorators = [snake.shifter.wrapper.node]


class DictCallHandler(dict[CallKey, Any], CallHandler):
    """Handler that just defers to dict to cache results."""

    pass


@pytest.mark.parametrize("decorator", decorators)
def test_simple_func(
    decorator: CallableDecorator,
) -> None:
    """Check we can construct a key, and cache in a dict."""

    @decorator
    def f(a: int, b: int) -> int:
        return a + b

    assert repr(key(f, 1, 2)) == f"{__name__}.f(a=1, b=2)"

    with Context(DictCallHandler()) as d:
        f(1, 2)
        f(1, 2)

    assert d[key(f, 1, 2)] == 3


@pytest.mark.parametrize("decorator", decorators)
def test_simple_failing_func(decorator: CallableDecorator) -> None:
    """Check we can construct a key, and cache in a dict."""
    # store a ref to the thrown exception outside the function
    # so we can check it's the same one returned
    exception = None

    @decorator
    def f(a: int, b: int) -> int:
        nonlocal exception
        # this exception should be cached by the wrapper
        # so we only see it once
        exception = RuntimeError("failure")

        raise exception

    with Context(DictCallHandler()) as d:
        try:
            f(1, 2)
        except RuntimeError as e:
            assert e is exception

        with pytest.raises(RuntimeError):
            f(1, 2)

    assert type(d[key(f, 1, 2)]) is Exception
    assert d[key(f, 1, 2)].args[0] is exception


@pytest.mark.parametrize("decorator", decorators)
def test_mock_null_handler(decorator: CallableDecorator) -> None:
    """Check that a null mock handler is called correctly."""
    handler = MagicMock()
    handler.__contains__.return_value = False
    handler.__getitem__.return_value = None
    handler.__setitem__.return_value = None

    @decorator
    def f(a: int, b: int) -> int:
        return a + b

    with Context(handler):
        assert f(1, 2) == 3

    handler.__contains__.assert_called_once_with(key(f, 1, 2))
    handler.__getitem__.assert_not_called()
    handler.__setitem__.assert_called_once_with(key(f, 1, 2), 3)


@pytest.mark.parametrize("decorator", decorators)
def test_mock_cached_handler(decorator: CallableDecorator) -> None:
    """Check that a fixed value mock handler is called correctly."""
    handler = MagicMock()
    handler.__contains__.return_value = True
    handler.__getitem__.return_value = Ellipsis
    handler.__setitem__.return_value = None

    @decorator
    def f(a: int, b: int) -> int:
        raise AssertionError("this functino should not be called")

    with pytest.raises(AssertionError):
        f(1, 2)

    with Context(handler):
        assert f(1, 2) is Ellipsis

    print(handler.__getitem__.mock_calls)

    handler.__contains__.assert_called_once_with(key(f, 1, 2))
    handler.__getitem__.assert_called_once_with(key(f, 1, 2))
    handler.__setitem__.assert_not_called()
