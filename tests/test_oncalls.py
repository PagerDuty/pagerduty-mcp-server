import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.oncalls import Oncall, OncallQuery
from pagerduty_mcp.tools.oncalls import list_oncalls


class TestOncallTools(unittest.TestCase):
    """Test cases for oncall tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_oncall_response = {
            "escalation_policy": {
                "id": "EP123",
                "summary": "Engineering Escalation Policy",
            },
            "escalation_level": 1,
            "schedule": {
                "id": "SCHED123",
                "summary": "Primary On-Call Schedule",
                "type": "schedule_reference",
            },
            "user": {
                "id": "USER123",
                "summary": "John Doe - Senior Engineer",
                "type": "user_reference",
            },
            "start": "2023-12-01T00:00:00Z",
            "end": "2023-12-08T00:00:00Z",
        }

        cls.sample_oncalls_list_response = [
            {
                "escalation_policy": {
                    "id": "EP123",
                    "summary": "Engineering Escalation Policy",
                },
                "escalation_level": 1,
                "schedule": {
                    "id": "SCHED123",
                    "summary": "Primary On-Call Schedule",
                    "type": "schedule_reference",
                },
                "user": {
                    "id": "USER123",
                    "summary": "John Doe - Senior Engineer",
                    "type": "user_reference",
                },
                "start": "2023-12-01T00:00:00Z",
                "end": "2023-12-08T00:00:00Z",
            },
            {
                "escalation_policy": {
                    "id": "EP456",
                    "summary": "DevOps Escalation Policy",
                },
                "escalation_level": 2,
                "schedule": {
                    "id": "SCHED456",
                    "summary": "Secondary On-Call Schedule",
                    "type": "schedule_reference",
                },
                "user": {
                    "id": "USER456",
                    "summary": "Jane Smith - Team Lead",
                    "type": "user_reference",
                },
                "start": "2023-12-08T00:00:00Z",
                "end": "2023-12-15T00:00:00Z",
            },
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_no_query_model(self, mock_get_client, mock_paginate):
        """Test that list_oncalls can be called with no arguments (no query_model)."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        result = list_oncalls()

        expected_params = {"earliest": "true", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_no_filters(self, mock_get_client, mock_paginate):
        """Test listing oncalls without any filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        query = OncallQuery()
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {"earliest": "true", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], Oncall)
        self.assertIsInstance(result.response[1], Oncall)
        self.assertEqual(result.response[0].user.id, "USER123")
        self.assertEqual(result.response[1].user.id, "USER456")
        self.assertEqual(result.response[0].escalation_level, 1)
        self.assertEqual(result.response[1].escalation_level, 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_time_zone(self, mock_get_client, mock_paginate):
        """Test listing oncalls with time zone filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        query = OncallQuery(time_zone="America/New_York")
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "time_zone": "America/New_York",
            "earliest": "true",
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_user_filter(self, mock_get_client, mock_paginate):
        """Test listing oncalls with user filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_oncalls_list_response[0]]

        query = OncallQuery(user_ids=["USER123"])
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "user_ids[]": ["USER123"],
            "earliest": "true",
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].user.id, "USER123")

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_escalation_policy_filter(self, mock_get_client, mock_paginate):
        """Test listing oncalls with escalation policy filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_oncalls_list_response[0]]

        query = OncallQuery(escalation_policy_ids=["EP123"])
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "escalation_policy_ids[]": ["EP123"],
            "earliest": "true",
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].escalation_policy.id, "EP123")

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_schedule_filter(self, mock_get_client, mock_paginate):
        """Test listing oncalls with schedule filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_oncalls_list_response[0]]

        query = OncallQuery(schedule_ids=["SCHED123"])
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "schedule_ids[]": ["SCHED123"],
            "earliest": "true",
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].schedule.id, "SCHED123")

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_time_range(self, mock_get_client, mock_paginate):
        """Test listing oncalls with time range filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        since_time = datetime(2023, 12, 1)
        until_time = datetime(2023, 12, 31)
        query = OncallQuery(since=since_time, until=until_time)
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "since": "2023-12-01T00:00:00",
            "until": "2023-12-31T00:00:00",
            "earliest": "true",
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_earliest_false(self, mock_get_client, mock_paginate):
        """Test listing oncalls with earliest set to false."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        query = OncallQuery(earliest=False)
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {"earliest": "false", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_all_filters(self, mock_get_client, mock_paginate):
        """Test listing oncalls with all filters applied."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_oncalls_list_response[0]]

        since_time = datetime(2023, 12, 1)
        until_time = datetime(2023, 12, 8)
        query = OncallQuery(
            time_zone="America/New_York",
            user_ids=["USER123"],
            escalation_policy_ids=["EP123"],
            schedule_ids=["SCHED123"],
            since=since_time,
            until=until_time,
            earliest=True,
            limit=50,
        )
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "time_zone": "America/New_York",
            "user_ids[]": ["USER123"],
            "escalation_policy_ids[]": ["EP123"],
            "schedule_ids[]": ["SCHED123"],
            "since": "2023-12-01T00:00:00",
            "until": "2023-12-08T00:00:00",
            "earliest": "true",
            "limit": 50,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing oncalls with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        query = OncallQuery(limit=100)
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {"earliest": "true", "limit": 100}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_empty_response(self, mock_get_client, mock_paginate):
        """Test listing oncalls when paginate returns empty list."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        query = OncallQuery(user_ids=["NONEXISTENT_USER"])
        result = list_oncalls(query)

        # Verify paginate call
        expected_params = {
            "user_ids[]": ["NONEXISTENT_USER"],
            "earliest": "true",
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="oncalls", params=expected_params)

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_paginate_error(self, mock_get_client, mock_paginate):
        """Test list_oncalls when paginate raises an exception."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("Pagination Error")

        query = OncallQuery()

        with self.assertRaises(Exception) as context:
            list_oncalls(query)

        self.assertEqual(str(context.exception), "Pagination Error")

    def test_oncall_query_to_params_all_fields(self):
        """Test OncallQuery.to_params() with all fields set."""
        since_time = datetime(2023, 12, 1, 10, 30, 45)
        until_time = datetime(2023, 12, 31, 18, 15, 20)

        query = OncallQuery(
            time_zone="America/New_York",
            user_ids=["USER1", "USER2"],
            escalation_policy_ids=["EP1", "EP2"],
            schedule_ids=["SCHED1", "SCHED2"],
            since=since_time,
            until=until_time,
            earliest=False,
            limit=25,
        )

        params = query.to_params()

        expected_params = {
            "time_zone": "America/New_York",
            "user_ids[]": ["USER1", "USER2"],
            "escalation_policy_ids[]": ["EP1", "EP2"],
            "schedule_ids[]": ["SCHED1", "SCHED2"],
            "since": "2023-12-01T10:30:45",
            "until": "2023-12-31T18:15:20",
            "earliest": "false",
            "limit": 25,
        }
        self.assertEqual(params, expected_params)

    def test_oncall_query_to_params_partial_fields(self):
        """Test OncallQuery.to_params() with only some fields set."""
        query = OncallQuery(
            user_ids=["USER1"],
            schedule_ids=["SCHED1"],
            earliest=True,
            limit=None,
        )

        params = query.to_params()

        expected_params = {
            "user_ids[]": ["USER1"],
            "schedule_ids[]": ["SCHED1"],
            "earliest": "true",
        }
        self.assertEqual(params, expected_params)

    def test_oncall_query_to_params_empty(self):
        """Test OncallQuery.to_params() with no fields set."""
        query = OncallQuery()

        params = query.to_params()

        expected_params = {"earliest": "true", "limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_oncall_query_to_params_earliest_none(self):
        """Test OncallQuery.to_params() with earliest set to None."""
        query = OncallQuery(earliest=None)

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_oncall_query_validation_limit_bounds(self):
        """Test OncallQuery limit validation within bounds."""
        # Test minimum limit
        query = OncallQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = OncallQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = OncallQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)


    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_service_ids(self, mock_get_client, mock_paginate):
        """Test listing oncalls filtered by service IDs (resolves to EP IDs)."""
        mock_client = MagicMock()
        mock_client.rget.return_value = {
            "id": "PSVC123",
            "name": "My Service",
            "escalation_policy": {
                "id": "EP_RESOLVED",
                "summary": "Resolved EP",
            },
        }
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        query = OncallQuery(service_ids=["PSVC123"])
        result = list_oncalls(query)

        # Verify service was resolved
        mock_client.rget.assert_called_once_with("/services/PSVC123")

        # Verify EP ID was passed to paginate
        call_args = mock_paginate.call_args
        params = call_args[1]["params"]
        self.assertIn("escalation_policy_ids[]", params)
        self.assertIn("EP_RESOLVED", params["escalation_policy_ids[]"])

        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.oncalls.paginate")
    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_with_service_ids_and_ep_ids(self, mock_get_client, mock_paginate):
        """Test listing oncalls with both service_ids and escalation_policy_ids merges correctly."""
        mock_client = MagicMock()
        mock_client.rget.return_value = {
            "id": "PSVC123",
            "name": "My Service",
            "escalation_policy": {
                "id": "EP_FROM_SERVICE",
                "summary": "EP from Service",
            },
        }
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = self.sample_oncalls_list_response

        query = OncallQuery(escalation_policy_ids=["EP_EXPLICIT"], service_ids=["PSVC123"])
        list_oncalls(query)

        call_args = mock_paginate.call_args
        params = call_args[1]["params"]
        ep_ids = params["escalation_policy_ids[]"]
        self.assertIn("EP_EXPLICIT", ep_ids)
        self.assertIn("EP_FROM_SERVICE", ep_ids)
        self.assertEqual(len(ep_ids), 2)

    @patch("pagerduty_mcp.tools.oncalls.get_client")
    def test_list_oncalls_service_not_found(self, mock_get_client):
        """Test listing oncalls with invalid service ID propagates error."""
        mock_client = MagicMock()
        mock_client.rget.side_effect = Exception("Service not found")
        mock_get_client.return_value = mock_client

        query = OncallQuery(service_ids=["INVALID_SVC"])
        with self.assertRaises(Exception) as context:
            list_oncalls(query)

        self.assertEqual(str(context.exception), "Service not found")


if __name__ == "__main__":
    unittest.main()
