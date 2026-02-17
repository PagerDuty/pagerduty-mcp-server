
from unittest import TestCase
from unittest.mock import MagicMock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context import set_strategy
from pagerduty_mcp.context.context_strategy import ContextStrategy
from pagerduty_mcp.models.users import User

class TestContextStrategy(ContextStrategy):
    """A simple context strategy for testing purposes."""

    def __init__(self):
        self._context = MagicMock(MCPContext)
        self._context.client = MagicMock(RestApiV2Client)

    def with_user(self) -> None:
        self._context.user = MagicMock(User)

    def get_context(self) -> MCPContext:
        return self._context

class ContextTestCase(TestCase):
    def setUp(self):
        self.strategy = TestContextStrategy()
        set_strategy(self.strategy)

    @property
    def mock_client(self):
        return self.strategy.get_client()

    def with_user(self):
        self.strategy.with_user()


