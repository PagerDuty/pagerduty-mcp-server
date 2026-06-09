

from contextlib import contextmanager
from unittest.mock import MagicMock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context.context_strategy import ContextStrategy
from pagerduty_mcp.context.mcp_context import MCPContext


class MockContextStrategy(ContextStrategy):
    """A mock context strategy for testing purposes."""
    def __init__(self):
        self._context = MagicMock(MCPContext)
        self._client = MagicMock(RestApiV2Client)

        self._context.client = self._client

    @property
    def context(self) -> MCPContext:
        """Return the current context."""
        return self._context

    @property
    def client(self) -> MagicMock:
        """Return the current client."""
        return self._client

    @client.setter
    def client(self, value):
        """Set the current client."""
        self._client = value
        self._context.client = value

    @property
    def user(self):
        """Return the current user."""
        return self._context.user

    @user.setter
    def user(self, value):
        """Set the current user."""
        self._context.user = value

    @contextmanager
    def use_context(self, context: MCPContext):
        """Mock implementation of use_context."""
        self._context = context
        yield
