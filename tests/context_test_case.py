
from unittest import TestCase
from unittest.mock import MagicMock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context import ContextManager
from pagerduty_mcp.context.context_strategy import ContextStrategy
from pagerduty_mcp.models.users import User

class TestContextStrategy(ContextStrategy):
    """A simple context strategy for testing purposes."""

    _context: MCPContext

    def __init__(self):
        self._context = MagicMock(MCPContext)
        self._context.client = MagicMock(RestApiV2Client)

    @property
    def context(self) -> MCPContext:
        return self._context

    def with_user(self) -> None:
        self._context.user = MagicMock(User)
class ContextTestCase(TestCase):
    def setUp(self):
        self.strategy = TestContextStrategy()
        ContextManager.set_strategy(self.strategy)

    @property
    def mock_client(self):
        return self.strategy.context.client

    def with_user(self):
        self.strategy.with_user()


