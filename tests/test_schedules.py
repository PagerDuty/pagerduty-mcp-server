import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import UserReference
from pagerduty_mcp.models.schedules import (
    Override,
    Schedule, 
    ScheduleCreateData,
    ScheduleCreateRequest,
    ScheduleLayerCreate,
    ScheduleLayerRestriction,
    ScheduleLayerUser,
    ScheduleOverrideCreate, 
    ScheduleQuery
)
from pagerduty_mcp.models.users import User
from pagerduty_mcp.tools.schedules import (
    create_schedule,
    create_schedule_override,
    get_schedule,
    list_schedule_users,
    list_schedules,
)


class TestScheduleTools(unittest.TestCase):
    """Test cases for schedule tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_schedule_response = {
            "id": "SCHED123",
            "summary": "Primary On-Call Schedule",
            "name": "Primary On-Call",
            "description": "Main on-call rotation for engineering team",
            "time_zone": "America/New_York",
            "self_url": "https://api.pagerduty.com/schedules/SCHED123",
            "html_url": "https://mycompany.pagerduty.com/schedules/SCHED123",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-06-01T12:00:00Z",
            "users": [
                {"id": "USER123", "summary": "John Doe - Senior Engineer", "type": "user_reference"},
                {"id": "USER456", "summary": "Jane Smith - Team Lead", "type": "user_reference"},
            ],
            "teams": [
                {"id": "TEAM123", "summary": "Engineering Team", "type": "team_reference"},
            ],
        }
        
        cls.sample_schedule_layer_response = {
            "id": "LAYER123",
            "name": "Night Shift",
            "start": "2023-01-01T20:00:00Z",
            "end": None,
            "rotation_virtual_start": "2023-01-01T20:00:00Z",
            "rotation_turn_length_seconds": 86400,
            "users": [{"user": {"id": "USER123", "summary": "John Doe", "type": "user_reference"}}]
        }

        cls.sample_schedules_list_response = [
            {
                "id": "SCHED123",
                "summary": "Primary On-Call Schedule",
                "name": "Primary On-Call",
                "description": "Main on-call rotation for engineering team",
                "time_zone": "America/New_York",
            },
            {
                "id": "SCHED456",
                "summary": "Secondary On-Call Schedule",
                "name": "Secondary On-Call",
                "description": "Backup on-call rotation for engineering team",
                "time_zone": "America/New_York",
            },
        ]

        cls.sample_users_list_response = [
            {
                "id": "USER123",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "user",
                "teams": [],
            },
            {
                "id": "USER456",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "role": "admin",
                "teams": [],
            },
        ]

        cls.sample_override_response = {
            "id": "OVERRIDE123",
            "start": "2023-12-25T00:00:00Z",
            "end": "2023-12-26T00:00:00Z",
            "user": {"id": "USER789", "summary": "Holiday Coverage", "type": "user_reference"},
        }

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_no_filters(self, mock_get_client, mock_paginate):
        """Test listing schedules without any filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_schedules_list_response

        query = ScheduleQuery()
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], Schedule)
        self.assertIsInstance(result.response[1], Schedule)
        self.assertEqual(result.response[0].id, "SCHED123")
        self.assertEqual(result.response[1].id, "SCHED456")
        self.assertEqual(result.response[0].name, "Primary On-Call")
        self.assertEqual(result.response[1].name, "Secondary On-Call")

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_with_query_filter(self, mock_get_client, mock_paginate):
        """Test listing schedules with query filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_schedules_list_response[0]]

        query = ScheduleQuery(query="Primary")
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"query": "Primary", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Primary On-Call")

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_with_team_filter(self, mock_get_client, mock_paginate):
        """Test listing schedules with team filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_schedules_list_response

        query = ScheduleQuery(team_ids=["TEAM123"])
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"team_ids[]": ["TEAM123"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_with_user_filter(self, mock_get_client, mock_paginate):
        """Test listing schedules with user filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_schedules_list_response

        query = ScheduleQuery(user_ids=["USER123", "USER456"])
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"user_ids[]": ["USER123", "USER456"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_with_include_filter(self, mock_get_client, mock_paginate):
        """Test listing schedules with include filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_schedules_list_response

        query = ScheduleQuery(include=["schedule_layers"])
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"include[]": ["schedule_layers"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_with_all_filters(self, mock_get_client, mock_paginate):
        """Test listing schedules with all filters applied."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_schedules_list_response[0]]

        query = ScheduleQuery(
            query="Primary",
            team_ids=["TEAM123"],
            user_ids=["USER123"],
            include=["schedule_layers"],
            limit=50,
        )
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {
            "query": "Primary",
            "team_ids[]": ["TEAM123"],
            "user_ids[]": ["USER123"],
            "include[]": ["schedule_layers"],
            "limit": 50,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_with_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing schedules with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_schedules_list_response

        query = ScheduleQuery(limit=50)
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"limit": 50}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_empty_response(self, mock_get_client, mock_paginate):
        """Test listing schedules when paginate returns empty list."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        query = ScheduleQuery(query="NonExistentSchedule")
        result = list_schedules(query)

        # Verify paginate call
        expected_params = {"query": "NonExistentSchedule", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="schedules", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.schedules.paginate")
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedules_paginate_error(self, mock_get_client, mock_paginate):
        """Test list_schedules when paginate raises an exception."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("Pagination Error")

        query = ScheduleQuery()

        with self.assertRaises(Exception) as context:
            list_schedules(query)

        self.assertEqual(str(context.exception), "Pagination Error")

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_get_schedule_success(self, mock_get_client):
        """Test successful retrieval of a specific schedule."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_schedule_response

        result = get_schedule("SCHED123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/schedules/SCHED123")

        # Verify result
        self.assertIsInstance(result, Schedule)
        self.assertEqual(result.id, "SCHED123")
        self.assertEqual(result.name, "Primary On-Call")
        self.assertEqual(result.description, "Main on-call rotation for engineering team")
        self.assertEqual(result.summary, "Primary On-Call Schedule")
        self.assertEqual(result.time_zone, "America/New_York")
        self.assertEqual(result.type, "schedule")

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_get_schedule_client_error(self, mock_get_client):
        """Test get_schedule when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_schedule("SCHED123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/schedules/SCHED123")

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_override_success(self, mock_get_client):
        """Test successful creation of schedule override."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = self.sample_override_response

        # Create override request
        user_ref = UserReference(id="USER789", summary="Test User")
        override = Override(
            start=datetime(2024, 12, 25),
            end=datetime(2024, 12, 26),
            user=user_ref,
        )
        override_request = ScheduleOverrideCreate(overrides=[override])

        result = create_schedule_override("SCHED123", override_request)

        # Verify API call
        mock_get_client.assert_called_once()

        # Verify that datetime objects were converted to ISO format
        expected_json = override_request.model_dump()
        expected_json["overrides"][0]["start"] = "2024-12-25T00:00:00"
        expected_json["overrides"][0]["end"] = "2024-12-26T00:00:00"

        self.mock_client.rpost.assert_called_once_with("/schedules/SCHED123/overrides", json=expected_json)

        # Verify result
        self.assertEqual(result, self.sample_override_response)

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_override_multiple_overrides(self, mock_get_client):
        """Test creation of schedule override with multiple overrides."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = [self.sample_override_response, self.sample_override_response]

        # Create override request with multiple overrides
        user_ref1 = UserReference(id="USER789", summary="Test User 1")
        user_ref2 = UserReference(id="USER999", summary="Test User 2")

        override1 = Override(
            start=datetime(2024, 12, 25),
            end=datetime(2024, 12, 26),
            user=user_ref1,
        )
        override2 = Override(
            start=datetime(2024, 12, 30),
            end=datetime(2024, 12, 31),
            user=user_ref2,
        )
        override_request = ScheduleOverrideCreate(overrides=[override1, override2])

        result = create_schedule_override("SCHED123", override_request)

        # Verify API call
        mock_get_client.assert_called_once()

        # Verify that datetime objects were converted to ISO format for both overrides
        expected_json = override_request.model_dump()
        expected_json["overrides"][0]["start"] = "2024-12-25T00:00:00"
        expected_json["overrides"][0]["end"] = "2024-12-26T00:00:00"
        expected_json["overrides"][1]["start"] = "2024-12-30T00:00:00"
        expected_json["overrides"][1]["end"] = "2024-12-31T00:00:00"

        self.mock_client.rpost.assert_called_once_with("/schedules/SCHED123/overrides", json=expected_json)

        # Verify result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_override_client_error(self, mock_get_client):
        """Test create_schedule_override when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.side_effect = Exception("API Error")

        # Create override request
        user_ref = UserReference(id="USER789", summary="Holiday Coverage")
        override = Override(
            start=datetime(2024, 12, 25),
            end=datetime(2024, 12, 26),
            user=user_ref,
        )
        override_request = ScheduleOverrideCreate(overrides=[override])

        with self.assertRaises(Exception) as context:
            create_schedule_override("SCHED123", override_request)

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedule_users_success(self, mock_get_client):
        """Test successful listing of schedule users."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_users_list_response

        result = list_schedule_users("SCHED123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/schedules/SCHED123/users")

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], User)
        self.assertIsInstance(result.response[1], User)
        self.assertEqual(result.response[0].id, "USER123")
        self.assertEqual(result.response[1].id, "USER456")
        self.assertEqual(result.response[0].name, "John Doe")
        self.assertEqual(result.response[1].name, "Jane Smith")

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedule_users_empty_response(self, mock_get_client):
        """Test listing schedule users when schedule has no users."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = []

        result = list_schedule_users("SCHED123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/schedules/SCHED123/users")

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_list_schedule_users_client_error(self, mock_get_client):
        """Test list_schedule_users when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            list_schedule_users("SCHED123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/schedules/SCHED123/users")

    def test_schedule_query_to_params_all_fields(self):
        """Test ScheduleQuery.to_params() with all fields set."""
        query = ScheduleQuery(
            query="test schedule",
            team_ids=["TEAM1", "TEAM2"],
            user_ids=["USER1", "USER2"],
            include=["schedule_layers"],
            limit=25,
        )

        params = query.to_params()

        expected_params = {
            "query": "test schedule",
            "team_ids[]": ["TEAM1", "TEAM2"],
            "user_ids[]": ["USER1", "USER2"],
            "include[]": ["schedule_layers"],
            "limit": 25,
        }
        self.assertEqual(params, expected_params)

    def test_schedule_query_to_params_partial_fields(self):
        """Test ScheduleQuery.to_params() with only some fields set."""
        query = ScheduleQuery(query="test", team_ids=["TEAM1"], limit=None)

        params = query.to_params()

        expected_params = {"query": "test", "team_ids[]": ["TEAM1"]}
        self.assertEqual(params, expected_params)

    def test_schedule_query_to_params_empty(self):
        """Test ScheduleQuery.to_params() with no fields set."""
        query = ScheduleQuery()

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_schedule_query_validation_limit_bounds(self):
        """Test ScheduleQuery limit validation within bounds."""
        # Test minimum limit
        query = ScheduleQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = ScheduleQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = ScheduleQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)

    def test_schedule_model_computed_type(self):
        """Test Schedule model computed type property."""
        schedule = Schedule(
            summary="Test Schedule Summary",
            name="Test Schedule",
            time_zone="America/New_York",
        )

        self.assertEqual(schedule.type, "schedule")
        
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_success(self, mock_get_client):
        """Test successful schedule creation."""
        mock_get_client.return_value = self.mock_client
        
        # Create a mock response similar to the API's actual response
        mock_response = {"schedule": self.sample_schedule_response}
        self.mock_client.rpost.return_value = mock_response
        
        # Create a test schedule request
        user = UserReference(id="USER123", summary="John Doe")
        layer_user = ScheduleLayerUser(user=user)
        
        layer = ScheduleLayerCreate(
            name="Night Shift",
            start=datetime(2023, 1, 1, 20, 0),
            rotation_virtual_start=datetime(2023, 1, 1, 20, 0),
            rotation_turn_length_seconds=86400,
            users=[layer_user]
        )
        
        schedule_data = ScheduleCreateData(
            name="Engineering On-Call",
            time_zone="America/New_York",
            description="Primary engineering on-call rotation",
            schedule_layers=[layer]
        )
        
        request = ScheduleCreateRequest(schedule=schedule_data)
        
        result = create_schedule(request)
        
        # Verify API call
        mock_get_client.assert_called_once()
        
        # Verify API call was made (not checking exact parameters since datetime formatting happens inside)
        self.mock_client.rpost.assert_called_once()
        args, kwargs = self.mock_client.rpost.call_args
        self.assertEqual(args[0], "/schedules")
        self.assertEqual(kwargs["json"]["schedule"]["name"], "Engineering On-Call")
        
        # Verify result
        self.assertIsInstance(result, Schedule)
        self.assertEqual(result.id, "SCHED123")
        self.assertEqual(result.name, "Primary On-Call")
        
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_with_restrictions(self, mock_get_client):
        """Test schedule creation with restrictions."""
        mock_get_client.return_value = self.mock_client
        
        # Create a mock response
        mock_response = {"schedule": self.sample_schedule_response}
        self.mock_client.rpost.return_value = mock_response
        
        # Create a test schedule with restrictions
        restriction = ScheduleLayerRestriction(
            type="daily_restriction",
            start_time_of_day="09:00:00",
            duration_seconds=28800  # 8 hours
        )
        
        user = UserReference(id="USER123", summary="John Doe")
        layer_user = ScheduleLayerUser(user=user)
        
        layer = ScheduleLayerCreate(
            name="Business Hours",
            start=datetime(2023, 1, 1),
            rotation_virtual_start=datetime(2023, 1, 1),
            rotation_turn_length_seconds=604800,  # 1 week
            users=[layer_user],
            restrictions=[restriction]
        )
        
        schedule_data = ScheduleCreateData(
            name="Business Hours Coverage",
            time_zone="America/New_York",
            description="Coverage during business hours only",
            schedule_layers=[layer]
        )
        
        request = ScheduleCreateRequest(schedule=schedule_data)
        
        result = create_schedule(request)
        
        # Verify API call
        mock_get_client.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, Schedule)
        
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_api_error(self, mock_get_client):
        """Test create_schedule when API returns an error."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.side_effect = Exception("API Error")
        
        # Create a minimal test schedule
        user = UserReference(id="USER123", summary="John Doe")
        layer_user = ScheduleLayerUser(user=user)
        
        layer = ScheduleLayerCreate(
            name="Night Shift",
            start=datetime(2023, 1, 1, 20, 0),
            rotation_virtual_start=datetime(2023, 1, 1, 20, 0),
            rotation_turn_length_seconds=86400,
            users=[layer_user]
        )
        
        schedule_data = ScheduleCreateData(
            name="Engineering On-Call",
            time_zone="America/New_York",
            schedule_layers=[layer]
        )
        
        request = ScheduleCreateRequest(schedule=schedule_data)
        
        with self.assertRaises(Exception) as context:
            create_schedule(request)
        
        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once()
        
    @patch("pagerduty_mcp.tools.schedules.get_client")
    def test_create_schedule_direct_response(self, mock_get_client):
        """Test create_schedule when API returns direct schedule object."""
        mock_get_client.return_value = self.mock_client
        
        # Create a response without the "schedule" wrapper
        self.mock_client.rpost.return_value = self.sample_schedule_response
        
        # Create a minimal test schedule
        user = UserReference(id="USER123", summary="John Doe")
        layer_user = ScheduleLayerUser(user=user)
        
        layer = ScheduleLayerCreate(
            name="Night Shift",
            start=datetime(2023, 1, 1, 20, 0),
            rotation_virtual_start=datetime(2023, 1, 1, 20, 0),
            rotation_turn_length_seconds=86400,
            users=[layer_user]
        )
        
        schedule_data = ScheduleCreateData(
            name="Engineering On-Call",
            time_zone="America/New_York",
            schedule_layers=[layer]
        )
        
        request = ScheduleCreateRequest(schedule=schedule_data)
        
        result = create_schedule(request)
        
        # Verify result handling with direct response
        self.assertIsInstance(result, Schedule)
        self.assertEqual(result.id, "SCHED123")


if __name__ == "__main__":
    unittest.main()
