"""Construct a simple call graph and test it's accurate."""
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import MutableSet
from typing import Optional

import pytest

import snake.shifter.wrapper
from snake.shifter import Context
from snake.shifter import key
from snake.shifter.abc import CallHandler
from snake.shifter.abc import CallKey
from snake.shifter.abc import Decorator


decorators = [snake.shifter.wrapper.shift]


class ParentCallHandler(CallHandler):
    """Store the set of calls that each call makes."""

    stack: List[Optional[CallKey]]
    children: Dict[Optional[CallKey], MutableSet[CallKey]]

    def __init__(self) -> None:
        """Create a call stack, and start with an empty call."""
        self.stack = []
        self.parents = defaultdict(set)

    def __contains__(self, key: CallKey) -> bool:
        """Register call with the parent, push onto stack."""
        if self.stack:
            self.parents[key].add(self.stack[-1])
        self.stack.append(key)
        return False

    def __getitem__(self, key: CallKey) -> Any:
        """Never called, we don't intercept return values."""
        raise NotImplementedError

    def __setitem__(self, key: CallKey, value: Any) -> None:
        """Pop call from stack."""
        self.stack.pop()


@pytest.mark.parametrize("decorator", decorators)
def test_simple_parents(decorator: Decorator) -> None:
    """Verify we construct an accurate call graph."""

    @decorator
    def f(a: int, b: int) -> int:
        return a + b

    @decorator
    def g(a: int, b: int) -> int:
        return f(a, b)

    a = 1
    b = 2

    handler = ParentCallHandler()
    with Context(handler):
        g(a, b)

    assert handler.parents[key(g, a, b)] == set()
    assert handler.parents[key(f, a, b)] == {key(g, a, b)}
