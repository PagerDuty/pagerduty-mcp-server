from contextvars import ContextVar
from contextlib import contextmanager

from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.context_strategy import ContextStrategy


class RequestContextStrategy(ContextStrategy):
    """Request-scoped context using context vars."""

    def __init__(self):
        self._context_var: ContextVar[MCPContext] = ContextVar("mcp_request_context")

    @property
    def context(self) -> MCPContext:
        """Get the current context."""
        return self._context_var.get()

    @contextmanager
    def use_context(self, context: MCPContext):
        """Context manager to set a client for the duration of a request."""
        token = self._context_var.set(context)
        try:
            yield
        finally:
            self._context_var.reset(token)
