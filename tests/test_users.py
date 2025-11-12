import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import TeamReference
from pagerduty_mcp.models.users import User, UserQuery
from pagerduty_mcp.tools.users import get_user_data, list_users


class TestUserTools(unittest.TestCase):
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
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_get_user_data_success(self, mock_get_client):
        """Test successful retrieval of current user data."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_user_response

        result = get_user_data()

        # Verify API call
        mock_get_client.assert_called_once()
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

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_get_user_data_client_error(self, mock_get_client):
        """Test get_user_data when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_user_data()

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/users/me")

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_no_filters(self, mock_get_client):
        """Test listing users without any filters."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_users_list_response

        result = list_users(UserQuery())

        # Verify API call
        mock_get_client.assert_called_once()
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

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_with_query_filter(self, mock_get_client):
        """Test listing users with query filter."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = [self.sample_users_list_response[0]]

        result = list_users(UserQuery(query="John"))

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"query": "John", "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "John Doe")

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_with_teams_filter(self, mock_get_client):
        """Test listing users with teams filter."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = [self.sample_users_list_response[1]]

        team_ids = ["TEAM2", "TEAM3"]
        result = list_users(UserQuery(teams_ids=team_ids))

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"team_ids[]": team_ids, "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Jane Smith")

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_with_custom_limit(self, mock_get_client):
        """Test listing users with custom limit."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_users_list_response

        result = list_users(UserQuery(limit=50))

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"limit": 50}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_with_all_filters(self, mock_get_client):
        """Test listing users with all filters applied."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = [self.sample_users_list_response[0]]

        team_ids = ["TEAM1"]
        result = list_users(UserQuery(query="John", teams_ids=team_ids, limit=10))

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"query": "John", "team_ids[]": team_ids, "limit": 10}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "John Doe")

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_empty_response(self, mock_get_client):
        """Test listing users when API returns empty list."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = []

        result = list_users(UserQuery(query="NonExistentUser"))

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"query": "NonExistentUser", "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_client_error(self, mock_get_client):
        """Test list_users when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            list_users(UserQuery())

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    def test_user_query_to_params_all_fields(self):
        """Test UserQuery.to_params() with all fields set."""
        query = UserQuery(query="test query", teams_ids=["TEAM1", "TEAM2"], limit=25)

        params = query.to_params()

        expected_params = {"query": "test query", "team_ids[]": ["TEAM1", "TEAM2"], "limit": 25}
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

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_single_team_filter(self, mock_get_client):
        """Test listing users with single team in teams_ids filter."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = [self.sample_users_list_response[0]]

        result = list_users(UserQuery(teams_ids=["TEAM1"]))

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"team_ids[]": ["TEAM1"], "limit": DEFAULT_PAGINATION_LIMIT}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.users.get_client")
    def test_list_users_with_query_model(self, mock_get_client):
        """Test listing users using UserQuery model - FastMCP compatible approach."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_users_list_response

        # Test the new approach using UserQuery model
        query_model = UserQuery(query="John", teams_ids=["TEAM1"], limit=10)
        result = list_users(query_model)

        # Verify API call
        mock_get_client.assert_called_once()
        expected_params = {"query": "John", "team_ids[]": ["TEAM1"], "limit": 10}
        self.mock_client.rget.assert_called_once_with("/users", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)


if __name__ == "__main__":
    unittest.main()
