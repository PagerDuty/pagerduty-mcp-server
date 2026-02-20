import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import UserReference
from pagerduty_mcp.models.teams import Team, TeamCreate, TeamCreateRequest, TeamMemberAdd, TeamQuery
from pagerduty_mcp.models.users import User
from pagerduty_mcp.tools.teams import (
    add_team_member,
    create_team,
    delete_team,
    get_team,
    list_team_members,
    list_teams,
    remove_team_member,
    update_team,
)


class TestTeamTools(unittest.TestCase):
    """Test cases for team tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_team_response = {
            "id": "TEAM123",
            "summary": "Engineering Team - Backend Services",
            "name": "Backend Engineering",
            "description": "Team responsible for backend services and APIs",
            "type": "team",
        }

        cls.sample_teams_list_response = [
            {
                "id": "TEAM123",
                "summary": "Engineering Team - Backend Services",
                "name": "Backend Engineering",
                "description": "Team responsible for backend services and APIs",
                "type": "team",
            },
            {
                "id": "TEAM456",
                "summary": "DevOps Team - Infrastructure",
                "name": "DevOps",
                "description": "Team responsible for infrastructure and deployments",
                "type": "team",
            },
        ]

        cls.sample_user_data = {
            "id": "USER123",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "teams": [
                {"id": "TEAM123", "summary": "Engineering Team - Backend Services", "type": "team_reference"},
                {"id": "TEAM789", "summary": "QA Team", "type": "team_reference"},
            ],
        }

        cls.sample_team_members_response = [
            {"user": {"id": "USER123", "summary": "John Doe - Senior Engineer", "type": "user_reference"}},
            {"user": {"id": "USER456", "summary": "Jane Smith - Team Lead", "type": "user_reference"}},
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None
        self.mock_client.rput.side_effect = None
        self.mock_client.rdelete.side_effect = None
        self.mock_client.put.side_effect = None

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_teams_all_scope(self, mock_get_client, mock_paginate):
        """Test listing teams with 'all' scope."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_teams_list_response

        query = TeamQuery(scope="all")
        result = list_teams(query)

        # Verify paginate call
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="teams", params=query.to_params())

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], Team)
        self.assertIsInstance(result.response[1], Team)
        self.assertEqual(result.response[0].id, "TEAM123")
        self.assertEqual(result.response[1].id, "TEAM456")
        self.assertEqual(result.response[0].name, "Backend Engineering")
        self.assertEqual(result.response[1].name, "DevOps")

    @patch("pagerduty_mcp.tools.teams.get_user_data")
    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_teams_my_scope(self, mock_get_client, mock_paginate, mock_get_user_data):
        """Test listing teams with 'my' scope."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_teams_list_response
        mock_get_user_data.return_value = User.model_validate(self.sample_user_data)

        query = TeamQuery(scope="my")
        result = list_teams(query)

        # Verify get_user_data was called
        mock_get_user_data.assert_called_once()

        # Verify paginate call to get all teams
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="teams", params={})

        # Verify result - should only include teams user is member of
        self.assertEqual(len(result.response), 1)  # Only TEAM123 matches user's teams
        self.assertEqual(result.response[0].id, "TEAM123")
        self.assertEqual(result.response[0].name, "Backend Engineering")

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_teams_with_query_filter(self, mock_get_client, mock_paginate):
        """Test listing teams with query filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_teams_list_response[0]]

        query = TeamQuery(query="Backend", scope="all")
        result = list_teams(query)

        # Verify paginate call
        expected_params = {"query": "Backend", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="teams", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Backend Engineering")

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_teams_with_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing teams with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_teams_list_response

        query = TeamQuery(limit=50, scope="all")
        result = list_teams(query)

        # Verify paginate call
        expected_params = {"limit": 50}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="teams", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_teams_empty_response(self, mock_get_client, mock_paginate):
        """Test listing teams when paginate returns empty list."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        query = TeamQuery(query="NonExistentTeam", scope="all")
        result = list_teams(query)

        # Verify paginate call
        expected_params = {"query": "NonExistentTeam", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="teams", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_get_team_success(self, mock_get_client):
        """Test successful retrieval of a specific team."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_team_response

        result = get_team("TEAM123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/teams/TEAM123")

        # Verify result
        self.assertIsInstance(result, Team)
        self.assertEqual(result.id, "TEAM123")
        self.assertEqual(result.name, "Backend Engineering")
        self.assertEqual(result.description, "Team responsible for backend services and APIs")
        self.assertEqual(result.summary, "Engineering Team - Backend Services")
        self.assertEqual(result.type, "team")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_get_team_client_error(self, mock_get_client):
        """Test get_team when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_team("TEAM123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/teams/TEAM123")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_create_team_success_wrapped_response(self, mock_get_client):
        """Test successful team creation with wrapped response."""
        mock_get_client.return_value = self.mock_client
        # API response with team wrapped in 'team' key
        wrapped_response = {"team": self.sample_team_response}
        self.mock_client.rpost.return_value = wrapped_response

        # Create TeamCreateRequest instance
        team_data = TeamCreate(
            name="New Backend Team", description="New team for backend services", default_role="manager"
        )
        team_create = TeamCreateRequest(team=team_data)

        result = create_team(team_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once_with("/teams", json=team_create.model_dump())

        # Verify result
        self.assertIsInstance(result, Team)
        self.assertEqual(result.id, "TEAM123")
        self.assertEqual(result.name, "Backend Engineering")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_create_team_success_direct_response(self, mock_get_client):
        """Test successful team creation with direct response."""
        mock_get_client.return_value = self.mock_client
        # API response directly as team object
        self.mock_client.rpost.return_value = self.sample_team_response

        # Create TeamCreateRequest instance
        team_data = TeamCreate(
            name="New Backend Team", description="New team for backend services", default_role="manager"
        )
        team_create = TeamCreateRequest(team=team_data)

        result = create_team(team_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once_with("/teams", json=team_create.model_dump())

        # Verify result
        self.assertIsInstance(result, Team)
        self.assertEqual(result.id, "TEAM123")
        self.assertEqual(result.name, "Backend Engineering")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_create_team_client_error(self, mock_get_client):
        """Test create_team when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.side_effect = Exception("API Error")

        # Create TeamCreateRequest instance
        team_data = TeamCreate(name="New Backend Team", description="New team for backend services")
        team_create = TeamCreateRequest(team=team_data)

        with self.assertRaises(Exception) as context:
            create_team(team_create)

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_update_team_success_wrapped_response(self, mock_get_client):
        """Test successful team update with wrapped response."""
        mock_get_client.return_value = self.mock_client
        # API response with team wrapped in 'team' key
        updated_team = self.sample_team_response.copy()
        updated_team["name"] = "Updated Backend Team"
        wrapped_response = {"team": updated_team}
        self.mock_client.rput.return_value = wrapped_response

        # Create TeamCreateRequest instance for update
        team_data = TeamCreate(name="Updated Backend Team", description="Updated team description")
        team_update = TeamCreateRequest(team=team_data)

        result = update_team("TEAM123", team_update)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rput.assert_called_once_with("/teams/TEAM123", json=team_update.model_dump())

        # Verify result
        self.assertIsInstance(result, Team)
        self.assertEqual(result.id, "TEAM123")
        self.assertEqual(result.name, "Updated Backend Team")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_update_team_success_direct_response(self, mock_get_client):
        """Test successful team update with direct response."""
        mock_get_client.return_value = self.mock_client
        # API response directly as team object
        updated_team = self.sample_team_response.copy()
        updated_team["name"] = "Updated Backend Team"
        self.mock_client.rput.return_value = updated_team

        # Create TeamCreateRequest instance for update
        team_data = TeamCreate(name="Updated Backend Team", description="Updated team description")
        team_update = TeamCreateRequest(team=team_data)

        result = update_team("TEAM123", team_update)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rput.assert_called_once_with("/teams/TEAM123", json=team_update.model_dump())

        # Verify result
        self.assertIsInstance(result, Team)
        self.assertEqual(result.id, "TEAM123")
        self.assertEqual(result.name, "Updated Backend Team")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_update_team_client_error(self, mock_get_client):
        """Test update_team when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rput.side_effect = Exception("API Error")

        # Create TeamCreateRequest instance
        team_data = TeamCreate(name="Updated Backend Team", description="Updated team description")
        team_update = TeamCreateRequest(team=team_data)

        with self.assertRaises(Exception) as context:
            update_team("TEAM123", team_update)

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_delete_team_success(self, mock_get_client):
        """Test successful team deletion."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.return_value = None

        result = delete_team("TEAM123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rdelete.assert_called_once_with("/teams/TEAM123")

        # Verify result (should be None)
        self.assertIsNone(result)

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_delete_team_client_error(self, mock_get_client):
        """Test delete_team when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            delete_team("TEAM123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rdelete.assert_called_once_with("/teams/TEAM123")

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_team_members_success(self, mock_get_client, mock_paginate):
        """Test successful listing of team members."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_team_members_response

        result = list_team_members("TEAM123")

        # Verify paginate call
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="/teams/TEAM123/members", params={})

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], UserReference)
        self.assertIsInstance(result.response[1], UserReference)
        self.assertEqual(result.response[0].id, "USER123")
        self.assertEqual(result.response[1].id, "USER456")

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_team_members_empty_response(self, mock_get_client, mock_paginate):
        """Test listing team members when team has no members."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        result = list_team_members("TEAM123")

        # Verify paginate call
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="/teams/TEAM123/members", params={})

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.teams.paginate")
    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_list_team_members_paginate_error(self, mock_get_client, mock_paginate):
        """Test list_team_members when paginate raises an exception."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("Pagination Error")

        with self.assertRaises(Exception) as context:
            list_team_members("TEAM123")

        self.assertEqual(str(context.exception), "Pagination Error")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_add_team_member_success(self, mock_get_client):
        """Test successful addition of team member."""
        mock_get_client.return_value = self.mock_client
        # Mock a successful response
        mock_response = MagicMock()
        mock_response.__bool__ = lambda x: True  # Make response truthy
        self.mock_client.put.return_value = mock_response

        member_data = TeamMemberAdd(user_id="USER789", role="manager")
        result = add_team_member("TEAM123", member_data)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.put.assert_called_once_with("/teams/TEAM123/users/USER789", json=member_data.model_dump())

        # Verify result
        self.assertEqual(result, "Successfully added user to team")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_add_team_member_failure(self, mock_get_client):
        """Test failed addition of team member."""
        mock_get_client.return_value = self.mock_client
        # Mock a failed response
        mock_response = MagicMock()
        mock_response.__bool__ = lambda x: False  # Make response falsy
        mock_response.reason = "User not found"
        self.mock_client.put.return_value = mock_response

        member_data = TeamMemberAdd(user_id="USER789", role="manager")
        result = add_team_member("TEAM123", member_data)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.put.assert_called_once_with("/teams/TEAM123/users/USER789", json=member_data.model_dump())

        # Verify result
        self.assertEqual(result, "Failed to add user to team: User not found")

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_add_team_member_client_error(self, mock_get_client):
        """Test add_team_member when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.put.side_effect = Exception("API Error")

        member_data = TeamMemberAdd(user_id="USER789", role="manager")

        with self.assertRaises(Exception) as context:
            add_team_member("TEAM123", member_data)

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_remove_team_member_success(self, mock_get_client):
        """Test successful removal of team member."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.return_value = None

        result = remove_team_member("TEAM123", "USER789")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rdelete.assert_called_once_with("/teams/TEAM123/users/USER789")

        # Verify result (should be None)
        self.assertIsNone(result)

    @patch("pagerduty_mcp.tools.teams.get_client")
    def test_remove_team_member_client_error(self, mock_get_client):
        """Test remove_team_member when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            remove_team_member("TEAM123", "USER789")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rdelete.assert_called_once_with("/teams/TEAM123/users/USER789")

    def test_team_query_to_params_all_fields(self):
        """Test TeamQuery.to_params() with all fields set."""
        query = TeamQuery(scope="all", query="test team", limit=25)

        params = query.to_params()

        expected_params = {"query": "test team", "limit": 25}
        self.assertEqual(params, expected_params)

    def test_team_query_to_params_partial_fields(self):
        """Test TeamQuery.to_params() with only some fields set."""
        query = TeamQuery(query="test", limit=None)

        params = query.to_params()

        expected_params = {"query": "test"}
        self.assertEqual(params, expected_params)

    def test_team_query_to_params_empty(self):
        """Test TeamQuery.to_params() with no fields set."""
        query = TeamQuery()

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_team_query_validation_limit_bounds(self):
        """Test TeamQuery limit validation within bounds."""
        # Test minimum limit
        query = TeamQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = TeamQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = TeamQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)

    def test_team_model_computed_type(self):
        """Test Team model computed type property."""
        team = Team(name="Test Team", description="Test Description")

        self.assertEqual(team.type, "team")


if __name__ == "__main__":
    unittest.main()
