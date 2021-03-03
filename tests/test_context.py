"""Test simple handler and context combinations."""
import pytest

from snake.shifter.context import Context
from snake.shifter.context import get_handler
from snake.shifter.context import NullHandler
from snake.shifter.typing import CallKey


def test_null_handler() -> None:
    """Check null handlers does nothing."""
    null = NullHandler()

    key = CallKey((id, 1))

    assert null.__contains__(key) is False
    with pytest.raises(NotImplementedError):
        null.__getitem__(key)

    null.__setitem__(key, 2)
    assert null.__contains__(key) is False


def test_context_push() -> None:
    """Check we can insert a null handler into the context stack."""
    handler = NullHandler()

    with Context(handler):
        assert get_handler() is handler

    assert get_handler() is not handler
