"""Check that constructed key types work correctly."""
from snake.shifter.key_type import make_key_type


def test_equality() -> None:
    """Verify that key hashes are sensible - namedtuples are not."""

    def f(a: int, b: int) -> int:
        return a + b

    def g(a: int, b: int) -> int:
        return f(a, b)

    f_type = make_key_type(f)
    g_type = make_key_type(g)

    assert f_type.__func__ is f  # type: ignore
    assert g_type.__func__ is g  # type: ignore

    assert f_type is not g_type
    assert f_type != g_type
    assert f_type(1, 2) is not g_type(1, 2)

    assert hash(f_type(1, 2)) != hash(g_type(1, 2))
    assert f_type(1, 2) != g_type(1, 2)
    assert f_type(1, 2) == f_type(1, 2)

    d = {}

    d[f_type(1, 2)] = 1
    d[g_type(1, 2)] = 2

    assert len(d) == 2


def test_repr() -> None:
    """Check we get a nice printable signature."""

    def f(a: int, b: int) -> int:
        return a + b

    f_type = make_key_type(f)

    assert repr(f_type(1, 2)) == "tests.test_key_type.f(a=1, b=2)"
