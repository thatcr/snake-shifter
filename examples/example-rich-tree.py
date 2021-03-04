"""Construct a rich tree from a call graph."""
from rich import print
from rich.tree import Tree

from snake.shifter import Context
from snake.shifter import shift


@shift
def f(a, b):
    return a + b


@shift
def g(a, b):
    return f(a, b) + f(b, a)


class RichTreeCallHandler:
    def __init__(self):
        self.stack = [Tree("Calls", highlight=True)]
        self.seen = set()

    def __contains__(self, key):
        if self.stack[-1] is not None:
            branch = self.stack[-1].add(
                key, style=("bold" if key not in self.seen else "#7F7F7F")
            )
        self.stack.append(branch)
        return False

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        self.seen.add(key)
        branch = self.stack.pop(-1)
        branch.label = repr(key) + " = " + repr(value)


with Context(RichTreeCallHandler()) as handler:
    g(1, 2)
print(handler.stack[0])


@shift
def fib(n):
    if n < 2:
        return 1
    return fib(n - 1) + fib(n - 2)


with Context(RichTreeCallHandler()) as handler:
    fib(7)
print(handler.stack[0])
