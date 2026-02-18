from typing import Optional
from contextvars import ContextVar
from contextlib import contextmanager

from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.context_strategy import ContextStrategy


class RequestContextStrategy(ContextStrategy):
    """Request-scoped context using context vars."""

    def __init__(self):
        self._context_var: ContextVar[Optional[MCPContext]] = ContextVar(
            'mcp_request_context',
            default=None
        )

    def get_context(self) -> MCPContext:
        context = self._context_var.get()
        if context is None:
            raise RuntimeError("No context set for request-scoped strategy")
        return context

    @contextmanager
    def with_client(self, client: RestApiV2Client):
        """Context manager to set the client for the duration of a request."""
        context = MCPContext(client=client)
        token = self._context_var.set(context)
        try:
            yield
        finally:
            self._context_var.reset(token)

    @contextmanager
    def with_context(self, context: MCPContext):
        """Context manager to set a full context for the duration of a request."""
        token = self._context_var.set(context)
        try:
            yield
        finally:
            self._context_var.reset(token)
