import pytest

from unittest.mock import MagicMock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context import ContextManager, application_context_strategy, get_client
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.request_context_strategy import RequestContextStrategy
from pagerduty_mcp.models.users import User

@pytest.fixture
def prepare_env(monkeypatch):
    """Fixture to set a specific environment variable."""
    monkeypatch.setenv("MCP_CONTEXT_STRATEGY", "RequestContextStrategy")
    yield
    ContextManager._context_strategy = None

@pytest.fixture
def mock_client(monkeypatch):
    mock_client = MagicMock(RestApiV2Client)
    mock_client.headers = {}

    monkeypatch.setattr(application_context_strategy, "PagerdutyMCPClient", lambda _: mock_client)
    return mock_client

@pytest.fixture
def mock_user(mock_client):
    user_fields = {"email": "test@example.com", "name": "blah", "role": "admin", "teams": []}
    mock_user = User(**user_fields)

    mock_client.rget.return_value = user_fields

    return mock_user

class TestRequestContextStrategy:
    """Test cases for the RequestContextStrategy and its integration with MCPContext."""

    def test_initialization(self, prepare_env):
        """Test that the RequestContextStrategy initializes the context correctly."""
        strategy = ContextManager.get_strategy()
        assert isinstance(strategy, RequestContextStrategy)

    def test_use_context_sets_user(self, prepare_env, mock_user, mock_client):
        context = MCPContext(mock_client)
        strategy = ContextManager.get_strategy()

        with strategy.use_context(context):
             assert ContextManager.get_user() == mock_user

        # indulge my light paranoia
        context = MCPContext(MagicMock(RestApiV2Client))
        with strategy.use_context(context):
             assert ContextManager.get_user() == None

    def test_get_client(self, prepare_env, mock_client):
        mock_context = MCPContext(mock_client)
        strategy = ContextManager.get_strategy()

        with strategy.use_context(mock_context):
            assert get_client() == mock_context.client

        # indulge my light paranoia
        context = MCPContext(MagicMock(RestApiV2Client))
        with strategy.use_context(context):
            assert get_client() != mock_context.client

    def test_raises_when_no_context(self, prepare_env):
        with pytest.raises(RuntimeError):
            ContextManager.get_client()

        with pytest.raises(RuntimeError):
            ContextManager.get_user()
