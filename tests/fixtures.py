"""Test fixtures and utilities for PagerDuty MCP server tests."""

import pytest
from unittest.mock import MagicMock, Mock

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.models import MCPContext, User, TeamReference


class MockContext:
    """Mock context that mimics the FastMCP Context behavior."""

    def __init__(self, client=None, user=None):
        """Initialize mock context with client and optional user.

        Args:
            client: Mock PagerDuty REST API client
            user: Optional mock user for user-scoped operations
        """
        # Create the mock client if not provided
        if client is None:
            client = MagicMock(spec=RestApiV2Client)

        # Create MCPContext with client and user
        mcp_context = MCPContext(client=client, user=user)

        # Create mock request_context.lifespan_context structure
        self.request_context = Mock()
        self.request_context.lifespan_context = mcp_context


@pytest.fixture
def mock_context_with_client_only(mock_client):
    """Provide mock context with client but no user (account-level auth)."""
    return MockContext(client=mock_client, user=None)


@pytest.fixture
def mock_context_with_user(mock_client, mock_user):
    """Provide mock context with both client and user (user-level auth)."""
    return MockContext(client=mock_client, user=mock_user)


@pytest.fixture
def sample_service():
    """Sample service data for testing."""
    return {
        "id": "PSERVICE1",
        "summary": "Test Service",
        "name": "Test Service",
        "type": "service",
        "status": "active"
    }


@pytest.fixture
def sample_incident():
    """Sample incident data for testing."""
    return {
        "id": "PINCIDENT1",
        "summary": "Test Incident",
        "title": "Test Incident Title",
        "status": "triggered",
        "urgency": "high",
        "service": {
            "id": "PSERVICE1",
            "summary": "Test Service",
            "type": "service_reference"
        }
    }


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "id": "USER123",
        "summary": "John Doe - Senior Engineer",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "role": "user",
        "teams": [
            {"id": "TEAM1", "summary": "Engineering Team", "type": "team_reference"}
        ]
    }


@pytest.fixture
def sample_team():
    """Sample team data for testing."""
    return {
        "id": "TEAM1",
        "summary": "Engineering Team",
        "name": "Engineering Team",
        "type": "team"
    }


class ContextTestCase:
    """Base test case class that provides context fixtures for unittest.TestCase subclasses.

    This allows existing unittest-based tests to easily use the new context fixtures.
    """

    def create_mock_context(self, client=None, user=None):
        """Create a mock context for testing.

        Args:
            client: Optional mock client (creates one if None)
            user: Optional mock user for user-scoped operations

        Returns:
            MockContext instance
        """
        return MockContext(client=client, user=user)

    def create_mock_client(self):
        """Create a fresh mock client with proper spec."""
        client = MagicMock(spec=RestApiV2Client)
        return client

    def create_mock_user(self):
        """Create a mock user."""
        return User(
            id="USER123",
            summary="John Doe - Test User",
            name="John Doe",
            email="john.doe@example.com",
            role="user",
            teams=[
                TeamReference(id="TEAM1", summary="Test Team")
            ]
        )