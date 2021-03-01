"""Construct a simple caller/callee graph and test it's accurate."""
from collections import defaultdict

import pytest

import snake.shifter.wrapper
from snake.shifter import CallHandler
from snake.shifter import Context
from snake.shifter import key


decorators = [snake.shifter.wrapper.shift]


class ParentCallHandler(CallHandler):
    def __init__(self):
        self.stack = defaultdict(set)
        self.parents = dict()

    def __contains__(self, key):
        self.parents[self.stack[-1]].add(key)
        self.stack.append(key)
        self.parents[key] = set()
        return False

    def __getitem__(self, key):
        return NotImplemented

    def __setitem__(self, key, value):
        self.stack.pop()


@pytest.mark.parametrize("decorator", decorators)
def test_simple_parents(decorator):
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

    assert key(f, a, b) in handler.parents
    assert handler.parents[key(f, a, b)] == set()
    assert handler.parents[key(g, a, b)] == {key(f, a, b)}
