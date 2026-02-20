import pytest

from unittest.mock import MagicMock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context import ContextManager, get_client, application_context_strategy
from pagerduty_mcp.context.application_context_strategy import ApplicationContextStrategy
from pagerduty_mcp.models.users import User


@pytest.fixture
def prepare_env(monkeypatch):
    """Fixture to set a specific environment variable."""
    monkeypatch.delenv("MCP_CONTEXT_STRATEGY", raising=False)
    monkeypatch.setenv("PAGERDUTY_USER_API_KEY", "test_api_key")

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


class TestApplicationContextStrategy:
    """Test cases for the ApplicationContextStrategy and its integration with MCPContext."""

    def test_initialization(self, prepare_env, mock_client, mock_user):
        """Test that the ApplicationContextStrategy initializes the context correctly."""
        strategy = ContextManager.get_strategy()
        assert isinstance(strategy, ApplicationContextStrategy)

        assert strategy.context.client == mock_client
        assert strategy.context.user == mock_user

    def test_get_client(self, prepare_env, mock_client):
        """Test that the client can be accessed through the context strategy."""
        assert get_client() == mock_client

    def test_get_client_no_api_key(self):
        with pytest.raises(RuntimeError):
            ContextManager.get_strategy()
