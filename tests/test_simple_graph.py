"""Construct a simple caller/callee graph and test it's accurate."""
import pytest

import snake.shifter.wrapper
from snake.shifter import CallHandler
from snake.shifter import Context
from snake.shifter import key


decorators = [snake.shifter.wrapper.shift]


class ParentCallHandler(CallHandler):
    """Store the set of calls that each call makes."""

    def __init__(self):
        """Create a call stack, and start with an empty call."""
        self.stack = [None]
        self.parents = {None: set()}

    def __contains__(self, key):
        """Register call with the parent, push onto stack."""
        self.parents[self.stack[-1]].add(key)
        self.stack.append(key)
        self.parents[key] = set()
        return False

    def __getitem__(self, key):
        """Never called, we don't intercept return values."""
        return NotImplemented

    def __setitem__(self, key, value):
        """Pop call from stack."""
        self.stack.pop()


@pytest.mark.parametrize("decorator", decorators)
def test_simple_parents(decorator):
    """Verify we construct an accurate call graph."""

    @decorator
    def f(a, b):
        return a + b

    @decorator
    def g(a, b):
        return f(a, b)

    a = 1
    b = 2

    with Context(ParentCallHandler()) as handler:
        g(a, b)

    assert None in handler.parents
    assert handler.parents[key(f, a, b)] == set()
    assert handler.parents[key(g, a, b)] == {key(f, a, b)}
    assert handler.parents[None] == {key(g, a, b)}

    assert key(f, a, b) in handler.parents
