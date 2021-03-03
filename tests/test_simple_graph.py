"""Construct a simple call graph and test it's accurate."""
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import MutableSet
from typing import Optional

from snake.shifter import Context
from snake.shifter import key
from snake.shifter.abc import CallHandler
from snake.shifter.abc import CallKey
from snake.shifter.abc import Decorator


class GraphCallHandler(CallHandler):
    """Store the set of calls that each call makes."""

    stack: List[Optional[CallKey]]
    parents: Dict[CallKey, MutableSet[Optional[CallKey]]]
    children: Dict[Optional[CallKey], MutableSet[CallKey]]

    retvals: Dict[CallKey, Any]

    def __init__(self) -> None:
        """Create a call stack, and start with an empty call."""
        self.stack = [None]
        self.parents = defaultdict(set)
        self.children = defaultdict(set)
        self.retvals = dict()

    def __contains__(self, key: CallKey) -> bool:
        """Register call with the parent, push onto stack."""
        self.children[self.stack[-1]].add(key)
        self.parents[key].add(self.stack[-1])

        if key in self.retvals:
            return self.retvals[key]

        self.stack.append(key)
        return False

    def __getitem__(self, key: CallKey) -> Any:
        """Never called, we don't intercept return values."""
        return self.retvals[key]

    def __setitem__(self, key: CallKey, value: Any) -> None:
        """Pop call from stack."""
        self.retvals[key] = value
        self.stack.pop()


def test_simple_graph(decorator: Decorator) -> None:
    """Verify we construct an accurate call graph."""

    @decorator
    def f(a: int, b: int) -> int:
        return a + b

    @decorator
    def g(a: int, b: int) -> int:
        return f(a, b)

    a = 1
    b = 2

    handler = GraphCallHandler()
    with Context(handler):
        g(a, b)

    assert handler.parents[key(g, a, b)] == {None}
    assert handler.parents[key(f, a, b)] == {key(g, a, b)}

    assert None in handler.children
    assert handler.children[key(f, a, b)] == set()
    assert handler.children[key(g, a, b)] == {key(f, a, b)}
    assert handler.children[None] == {key(g, a, b)}

    assert key(f, a, b) in handler.children

    assert key(f, a, b) in handler.retvals
    assert key(g, a, b) in handler.retvals
    assert handler.retvals[key(f, a, b)] == a + b
    assert handler.retvals[key(g, a, b)] == a + b
