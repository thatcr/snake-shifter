"""Common fixures for testing snake-shifter."""
import sys

import pytest
from _pytest.python import Metafunc
from rich.console import Console


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Map decorator fixture to list of decorators to test."""
    import snake.shifter.wrapper

    decorators = [snake.shifter.wrapper.shift]

    if "decorator" in metafunc.fixturenames:
        metafunc.parametrize(
            "decorator", decorators, ids=[d.__module__ for d in decorators]
        )


@pytest.fixture(autouse=True, scope="session")
def _rich_print(request):
    """Create a full-color rich terminal for logging."""
    request.console = Console(
        force_terminal=True,
        force_interactive=False,
        file=sys.stdout,
        record=False,
    )
    old_print = __builtins__["print"]
    __builtins__["print"] = request.console.print

    yield request.console.print

    __builtins__["print"] = old_print
