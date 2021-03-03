"""Common fixures for testing snake-shifter."""
from _pytest.python import Metafunc

import snake.shifter.wrapper


decorators = [snake.shifter.wrapper.shift]


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Map decorator fixture to list of decorators to test."""
    if "decorator" in metafunc.fixturenames:
        metafunc.parametrize(
            "decorator", decorators, ids=[d.__module__ for d in decorators]
        )
