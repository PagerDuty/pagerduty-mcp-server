from contextlib import contextmanager
from contextvars import ContextVar

from pagerduty_mcp.context.context_strategy import ContextData, ContextStrategy


class RequestContextStrategy(ContextStrategy):
    """Request-scoped context using context vars."""

    def __init__(self):
        self._context_var: ContextVar[ContextData] = ContextVar("mcp_request_context")

    @property
    def context(self) -> ContextData:
        """Get the current context."""
        return self._context_var.get()

    @contextmanager
    def use_context(self, context: ContextData):
        """Context manager to set a client for the duration of a request."""
        token = self._context_var.set(context)
        try:
            yield context
        finally:
            self._context_var.reset(token)
