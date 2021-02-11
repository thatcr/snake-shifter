"""Context manager and empty handler."""


class Context(object):
    """Context handler that maintains a stack of handlers."""

    def __init__(self, handler):
        """Initialize context with a handler instance."""
        self.handler = handler

    def __enter__(self):
        """Push the handler onto the global stack."""
        global _handlers
        _handlers.append(self.handler)
        return self.handler

    def __exit__(self, exc_type, exc_value_, traceback):
        """Remove handler from the global stack."""
        _handlers.pop(-1)


class NullHandler(object):
    """Handler that does nothing."""

    def __contains__(self, key):
        """Avoid handling anything."""
        return False

    def __getitem__(self, key):
        """We never cache any values on this handler."""
        raise NotImplementedError()

    def __setitem__(self, key, value):
        """Never process any function results."""
        pass


# global stack of handlers, tail element is used for t
# the active handler.
# TODO make this thread/coroutine safe
_handlers = [NullHandler()]


def get_handler():
    """Return the active handler at the top of the stack."""
    return _handlers[-1]
