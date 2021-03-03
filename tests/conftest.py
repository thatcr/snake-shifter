"""Common fixures for testing snake-shifter."""
from _pytest.python import Metafunc


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Map decorator fixture to list of decorators to test."""
    import snake.shifter.wrapper

    decorators = [snake.shifter.wrapper.shift]

    if "decorator" in metafunc.fixturenames:
        metafunc.parametrize(
            "decorator", decorators, ids=[d.__module__ for d in decorators]
        )
