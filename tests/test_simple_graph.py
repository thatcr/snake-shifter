"""Construct a simple call graph and test it's accurate."""
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Set

import pytest

from snake.shifter import Context
from snake.shifter import key
from snake.shifter.typing import CallKey
from snake.shifter.typing import Decorator


class GraphCallHandler:
    """Store the set of calls that each call makes."""

    stack: List[CallKey]
    parents: Dict[CallKey, Set[CallKey]]
    children: Dict[CallKey, Set[CallKey]]

    retvals: Dict[CallKey, Any]

    def __init__(self) -> None:
        """Create a call stack, and start with an empty call."""
        self.stack = []
        self.parents = defaultdict(set)
        self.children = defaultdict(set)
        self.retvals = dict()

    def __contains__(self, key: CallKey) -> bool:
        """Register call with the parent, push onto stack."""
        if self.stack:
            self.children[self.stack[-1]].add(key)
            self.parents[key].add(self.stack[-1])

        if key in self.retvals:
            return True

        self.stack.append(key)
        return False

    def __getitem__(self, key: CallKey) -> Any:
        """Never called, we don't intercept return values."""
        return self.retvals[key]

    def __setitem__(self, key: CallKey, value: Any) -> None:
        """Pop call from stack."""
        self.retvals[key] = value
        self.stack.pop()

    def bump(self, changes: Mapping[CallKey, Any]) -> "GraphCallHandler":
        """Create a new handler with some return values overridden."""
        handler = GraphCallHandler()

        handler.retvals = self.retvals.copy()

        # duplicate all the children of nodes we haven't bumped
        handler.children = defaultdict(
            set, {k: v.copy() for k, v in self.children.items()}
        )
        handler.parents = defaultdict(
            set, {k: v.copy() for k, v in self.parents.items()}
        )

        deps: List[CallKey] = list(changes.keys())
        for dep in deps:
            # if dep is not None:
            deps.extend(handler.parents.pop(dep, set()))
            handler.retvals.pop(dep, None)

            # remove the parent link from any children
            for child in handler.children.pop(dep, set()):
                if child in handler.parents:
                    handler.parents[child].remove(dep)

        # override cached values with bumps
        handler.retvals.update(changes)

        return handler


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
        g(a, b)

    assert handler.parents[key(g, a, b)] == set()
    assert handler.parents[key(f, a, b)] == {key(g, a, b)}

    assert handler.children[key(f, a, b)] == set()
    assert handler.children[key(g, a, b)] == {key(f, a, b)}

    assert key(f, a, b) in handler.children

    assert key(f, a, b) in handler.retvals
    assert key(g, a, b) in handler.retvals
    assert handler.retvals[key(f, a, b)] == a + b
    assert handler.retvals[key(g, a, b)] == a + b

    # tweak the cache, check it is used
    handler.retvals[key(g, a, b)] = 123
    with Context(handler):
        assert g(a, b) == 123


def test_simple_graph_exception(decorator: Decorator) -> None:
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

    @decorator
    def g(a: int, b: int) -> int:
        return f(a, b)

    a = 1
    b = 2

    handler = GraphCallHandler()
    with Context(handler):
        try:
            g(a, b)
        except RuntimeError as e:
            assert e is exception

        with pytest.raises(RuntimeError):
            g(a, b)

    # exceptions get cached twice - should this be the case, or do
    # we re-call an throw from source?
    assert type(handler.retvals[key(f, a, b)]) is Exception
    assert type(handler.retvals[key(g, a, b)]) is Exception
    assert handler.retvals[key(f, a, b)].args[0] is exception
    assert handler.retvals[key(g, a, b)].args[0] is exception

    assert handler.parents[key(g, a, b)] == set()
    assert handler.parents[key(f, a, b)] == {key(g, a, b)}


def test_simple_graph_bump(decorator: Decorator) -> None:
    """Try bumping some functions and check that the graph is consistent."""

    @decorator
    def f(x: int) -> int:
        return x

    @decorator
    def g(x: int, y: int) -> int:
        return f(x) + f(y)

    handler = GraphCallHandler()
    with Context(handler):
        assert g(1, 2) == 3
        assert g(1, 3) == 4

    print(handler.__dict__)

    bumped = handler.bump({key(f, 1): 10})
    with Context(bumped):
        print(bumped.__dict__)

        #
        assert bumped.parents == {key(f, 2): set(), key(f, 3): set()}

        # no nodes have any children left - we evicted them all
        assert not bumped.children
        assert bumped.retvals == {key(f, 2): 2, key(f, 3): 3, key(f, 1): 10}

        assert g(1, 2) == 12

    print(bumped.__dict__)
