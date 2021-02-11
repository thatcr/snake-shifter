"""Test simple handler and context combinations."""
import pytest

from snake.shifter.context import Context
from snake.shifter.context import get_handler
from snake.shifter.context import NullHandler


def test_null_handler():
    """Check null handlers does nothing."""
    null = NullHandler()

    assert null.__contains__(1) is False
    with pytest.raises(NotImplementedError):
        null.__getitem__(1)

    assert null.__setitem__(1, 2) is None


def test_context_push():
    """Check we can insert a null handler into the context stack."""
    handler = NullHandler()

    with Context(handler):
        assert get_handler() is handler

    assert get_handler() is not handler
