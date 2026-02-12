import unittest
from tests.fixtures import ContextTestCase
from unittest.mock import MagicMock

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import TeamReference
from pagerduty_mcp.models.users import User, UserQuery
from pagerduty_mcp.tools.users import get_user_data, list_users


class TestUserTools(unittest.TestCase, ContextTestCase):
    """Test cases for user tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_user_response = {
            "id": "USER123",
            "summary": "John Doe - Senior Engineer",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "teams": [
                {"id": "TEAM1", "summary": "Engineering Team", "type": "team_reference"},
                {"id": "TEAM2", "summary": "DevOps Team", "type": "team_reference"},
            ],
        }

        cls.sample_users_list_response = [
            {
                "id": "USER123",
                "summary": "John Doe - Senior Engineer",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "user",
                "teams": [{"id": "TEAM1", "summary": "Engineering Team", "type": "team_reference"}],
            },
            {
                "id": "USER456",
                "summary": "Jane Smith - Team Lead",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "role": "admin",
                "teams": [{"id": "TEAM2", "summary": "DevOps Team", "type": "team_reference"}],
            },
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Setup mock context and client for each test."""
        self.mock_client = self.create_mock_client()
        self.mock_context = self.create_mock_context(client=self.mock_client)

    def test_get_user_data_success(self):
        """Test successful retrieval of current user data."""
        self.mock_client.rget.return_value = self.sample_user_response

        result = get_user_data(ctx=self.mock_context)

        # Verify API call
        self.mock_client.rget.assert_called_once_with("/users/me")

        # Verify result
        self.assertIsInstance(result, User)
        self.assertEqual(result.id, "USER123")
        self.assertEqual(result.name, "John Doe")
        self.assertEqual(result.email, "john.doe@example.com")
        self.assertEqual(result.role, "user")
        self.assertEqual(result.summary, "John Doe - Senior Engineer")
        self.assertEqual(len(result.teams), 2)
        self.assertIsInstance(result.teams[0], TeamReference)
        self.assertEqual(result.teams[0].id, "TEAM1")
        self.assertEqual(result.teams[1].id, "TEAM2")
        self.assertEqual(result.type, "user")

    def test_get_user_data_client_error(self):
        """Test get_user_data when client raises an exception."""
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_user_data(ctx=self.mock_context)

        self.assertEqual(str(context.exception), "API Error")
        self.mock_client.rget.assert_called_once_with("/users/me")

    def test_list_users_no_filters(self):
        """Test listing users without any filters."""
        self.mock_client.rget.return_value = self.sample_users_list_response

        result = list_users(ctx=self.mock_context, query_model=UserQuery())

        # Verify API call
        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], User)
        self.assertIsInstance(result.response[1], User)
        self.assertEqual(result.response[0].id, "USER123")
        self.assertEqual(result.response[1].id, "USER456")
        self.assertEqual(result.response[0].name, "John Doe")
        self.assertEqual(result.response[1].name, "Jane Smith")

    def test_list_users_with_query_filter(self):
        """Test listing users with query filter."""
        self.mock_client.rget.return_value = [self.sample_users_list_response[0]]

        result = list_users(ctx=self.mock_context, query_model=UserQuery(query="John"))

        # Verify API call
        expected_params = {"query": "John", "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "John Doe")

    def test_list_users_with_teams_filter(self):
        """Test listing users with teams filter."""
        self.mock_client.rget.return_value = [self.sample_users_list_response[1]]

        team_ids = ["TEAM2", "TEAM3"]
        result = list_users(ctx=self.mock_context, query_model=UserQuery(teams_ids=team_ids))

        # Verify API call
        expected_params = {"teams_ids[]": team_ids, "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Jane Smith")

    def test_list_users_with_custom_limit(self):
        """Test listing users with custom limit."""
        self.mock_client.rget.return_value = self.sample_users_list_response

        result = list_users(ctx=self.mock_context, query_model=UserQuery(limit=50))

        # Verify API call
        expected_params = {"limit": 50}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    def test_list_users_with_all_filters(self):
        """Test listing users with all filters applied."""
        self.mock_client.rget.return_value = [self.sample_users_list_response[0]]

        team_ids = ["TEAM1"]
        result = list_users(ctx=self.mock_context, query_model=UserQuery(query="John", teams_ids=team_ids, limit=10))

        # Verify API call
        expected_params = {"query": "John", "teams_ids[]": team_ids, "limit": 10}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "John Doe")

    def test_list_users_empty_response(self):
        """Test listing users when API returns empty list."""
        self.mock_client.rget.return_value = []

        result = list_users(ctx=self.mock_context, query_model=UserQuery(query="NonExistentUser"))

        # Verify API call
        expected_params = {"query": "NonExistentUser", "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 0)

    def test_list_users_client_error(self):
        """Test list_users when client raises an exception."""
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            list_users(ctx=self.mock_context, query_model=UserQuery())

        self.assertEqual(str(context.exception), "API Error")

    def test_user_query_to_params_all_fields(self):
        """Test UserQuery.to_params() with all fields set."""
        query = UserQuery(query="test query", teams_ids=["TEAM1", "TEAM2"], limit=25)

        params = query.to_params()

        expected_params = {"query": "test query", "teams_ids[]": ["TEAM1", "TEAM2"], "limit": 25}
        self.assertEqual(params, expected_params)

    def test_user_query_to_params_partial_fields(self):
        """Test UserQuery.to_params() with only some fields set."""
        query = UserQuery(query="test", limit=None)

        params = query.to_params()

        expected_params = {"query": "test"}
        self.assertEqual(params, expected_params)

    def test_user_query_to_params_empty(self):
        """Test UserQuery.to_params() with no fields set."""
        query = UserQuery()

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_user_query_validation_limit_bounds(self):
        """Test UserQuery limit validation within bounds."""
        # Test minimum limit
        query = UserQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = UserQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = UserQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)

    def test_user_model_computed_type(self):
        """Test User model computed type property."""
        user = User(name="Test User", email="test@example.com", role="user", teams=[])

        self.assertEqual(user.type, "user")

    def test_list_users_single_team_filter(self):
        """Test listing users with single team in teams_ids filter."""
        self.mock_client.rget.return_value = [self.sample_users_list_response[0]]

        result = list_users(ctx=self.mock_context, query_model=UserQuery(teams_ids=["TEAM1"]))

        # Verify API call
        expected_params = {"teams_ids[]": ["TEAM1"], "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)

    def test_list_users_with_query_model(self):
        """Test listing users using UserQuery model - FastMCP compatible approach."""
        self.mock_client.rget.return_value = self.sample_users_list_response

        # Test the new approach using UserQuery model
        query_model = UserQuery(query="John", teams_ids=["TEAM1"], limit=10)
        result = list_users(ctx=self.mock_context, query_model=query_model)

        # Verify API call
        expected_params = {"query": "John", "teams_ids[]": ["TEAM1"], "limit": 10}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)


if __name__ == "__main__":
    unittest.main()
