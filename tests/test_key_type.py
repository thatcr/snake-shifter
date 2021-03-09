"""Check that constructed key types work correctly."""
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

from snake.shifter.key_type import make_key_type


def test_equality() -> None:
    """Verify that key hashes are sensible - namedtuples are not."""

    def f(a: int, b: int) -> int:
        ...

    def g(a: int, b: int) -> int:
        ...

    f_type = make_key_type(f)
    g_type = make_key_type(g)

    assert f_type.__func__ is f  # type: ignore
    assert g_type.__func__ is g  # type: ignore

    assert f_type is not g_type
    assert f_type != g_type
    assert f_type.from_call(1, 2) is not g_type.from_call(1, 2)

    assert hash(f_type.from_call(1, 2)) != hash(g_type.from_call(1, 2))
    assert f_type.from_call(1, 2) != g_type.from_call(1, 2)
    assert f_type.from_call(1, 2) == f_type.from_call(1, 2)

    d = {}

    d[f_type.from_call(1, 2)] = 1
    d[g_type.from_call(1, 2)] = 2

    assert len(d) == 2


def test_local_repr() -> None:
    """Check we get a nice printable signature."""

    def f(a: int, b: int, c: int = 3, d: Optional[None] = None) -> int:
        ...

    key_type = make_key_type(f)

    assert repr(key_type.from_call(1, 2)) == "f(a=1, b=2, c=3, d=None)"
    assert repr(key_type.from_call(1, 2, 5)) == "f(a=1, b=2, c=5, d=None)"
    assert repr(key_type.from_call(1, 2, c=4)) == "f(a=1, b=2, c=4, d=None)"
    assert repr(key_type.from_call(1, 2, d=10)) == "f(a=1, b=2, c=3, d=10)"
    assert repr(key_type.from_call(1, 2, c=4, d=10)) == "f(a=1, b=2, c=4, d=10)"


def f(a: int, b: int, c: int = 3, d: Optional[None] = None) -> int:
    """Test function to generate a module level key type."""
    ...


def test_module_repr() -> None:
    """Check we get a nice printable signature."""
    key_type = make_key_type(f)

    assert (
        repr(key_type.from_call(1, 2)) == "tests.test_key_type.f(a=1, b=2, c=3, d=None)"
    )
    assert (
        repr(key_type.from_call(1, 2, 5))
        == "tests.test_key_type.f(a=1, b=2, c=5, d=None)"
    )
    assert (
        repr(key_type.from_call(1, 2, c=4))
        == "tests.test_key_type.f(a=1, b=2, c=4, d=None)"
    )
    assert (
        repr(key_type.from_call(1, 2, d=10))
        == "tests.test_key_type.f(a=1, b=2, c=3, d=10)"
    )
    assert (
        repr(key_type.from_call(1, 2, c=4, d=10))
        == "tests.test_key_type.f(a=1, b=2, c=4, d=10)"
    )


def test_args() -> None:
    """Verify that positional variable arguments work."""

    def f(*args: Tuple[Any]) -> int:
        ...

    key_type = make_key_type(f)

    assert repr(key_type.from_call(1, 2)) == "f(args=(1, 2))"


def test_kwargs() -> None:
    """Verify that keyword variable arguments work."""

    def f(**kwargs: Dict[str, Any]) -> int:
        ...

    key_type = make_key_type(f)

    assert repr(key_type.from_call(a=1, b=2)) == "f(kwargs={'a': 1, 'b': 2})"
