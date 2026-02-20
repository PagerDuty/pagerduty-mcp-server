import pytest

from unittest.mock import MagicMock, patch

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context import ContextManager, get_client
from pagerduty_mcp.context.application_context_strategy import ApplicationContextStrategy
from pagerduty_mcp.models.users import User

@pytest.fixture
def prepare_env(monkeypatch):
    """Fixture to set a specific environment variable."""
    monkeypatch.delenv("MCP_CONTEXT_STRATEGY", raising=False)
    monkeypatch.setenv("PAGERDUTY_USER_API_KEY", "test_api_key")

    ContextManager._context_strategy = None

@pytest.fixture
def mock_client():
    mock_client = MagicMock(RestApiV2Client)
    mock_client.headers = {}
    return mock_client

@pytest.fixture
def mock_user(mock_client):
    user_fields = {"email": "test@example.com", "name": "blah", "role": "admin", "teams": []}
    mock_user = User(**user_fields)

    mock_client.rget.return_value = user_fields

    return mock_user

class TestApplicationContextStrategy:
    """Test cases for the ApplicationContextStrategy and its integration with MCPContext."""

    @patch("pagerduty_mcp.context.application_context_strategy.create_pd_client")
    def test_initialization(self, mock_create_pd_client, prepare_env, mock_client, mock_user):
        """Test that the ApplicationContextStrategy initializes the context correctly."""
        mock_create_pd_client.return_value = mock_client

        strategy = ContextManager.get_strategy()
        assert isinstance(strategy, ApplicationContextStrategy)

        assert strategy.context.client == mock_client
        assert strategy.context.user == mock_user

    @patch("pagerduty_mcp.context.application_context_strategy.create_pd_client")
    def test_get_client(self, mock_create_pd_client, prepare_env, mock_client):
        """Test that the client can be accessed through the context strategy."""
        mock_create_pd_client.return_value = mock_client

        assert get_client() == mock_client
