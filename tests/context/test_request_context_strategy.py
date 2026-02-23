import pytest

from unittest.mock import MagicMock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context import ContextResolver, application_context_strategy
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.request_context_strategy import RequestContextStrategy
from pagerduty_mcp.models.users import User

@pytest.fixture
def prepare_env(monkeypatch):
    """Fixture to set a specific environment variable."""
    yield
    ContextResolver._context_strategy = None

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

    def test_use_context_sets_user(self, prepare_env, mock_user, mock_client):
        context = MCPContext(mock_client)
        strategy = RequestContextStrategy()
        ContextResolver.set_strategy(strategy)

        with strategy.use_context(context):
             assert ContextResolver.get_user() == mock_user

        # also works from manager class
        with ContextResolver.use_context(context):
             assert ContextResolver.get_user() == mock_user

        # indulge my light paranoia
        context = MCPContext(MagicMock(RestApiV2Client))
        with strategy.use_context(context):
             assert ContextResolver.get_user() == None

    def test_get_client(self, prepare_env, mock_client):
        mock_context = MCPContext(mock_client)
        strategy = RequestContextStrategy()

        ContextResolver.set_strategy(strategy)

        with strategy.use_context(mock_context):
            assert ContextResolver.get_client() == mock_context.client

        # indulge my light paranoia
        context = MCPContext(MagicMock(RestApiV2Client))
        with strategy.use_context(context):
            assert ContextResolver.get_client() != mock_context.client

    def test_raises_when_no_context(self, prepare_env):
        ContextResolver.set_strategy(RequestContextStrategy())

        with pytest.raises(LookupError):
            ContextResolver.get_client()

        with pytest.raises(LookupError):
            ContextResolver.get_user()
