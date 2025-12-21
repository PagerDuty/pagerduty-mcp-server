import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.change_events import (
    ChangeEvent,
    ChangeEventQuery,
)
from pagerduty_mcp.models.references import IntegrationReference, ServiceReference
from pagerduty_mcp.tools.change_events import (
    get_change_event,
    list_change_events,
    list_incident_change_events,
    list_service_change_events,
)


class TestChangeEventTools(unittest.TestCase):
    """Test cases for change event tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_integration = {
            "id": "P0Z3BFB",
            "summary": None,
            "type": "inbound_integration_reference",
        }

        cls.sample_service = {
            "id": "P43PBXB",
            "summary": None,
            "type": "service_reference",
        }

        cls.sample_change_event_response = {
            "id": "01G6B73PTIFH786FXPLPEKWG5I",
            "summary": "Test change event from MCP server",
            "timestamp": "2025-11-24T20:45:55Z",
            "services": [cls.sample_service],
            "integration": cls.sample_integration,
            "routing_key": "bc0913066d5d4208c09f71ba1f030a03",
            "source": "mcp-server-test",
            "links": [
                {
                    "text": "PagerDuty MCP Server Repository",
                    "href": "https://github.com/PagerDuty/pagerduty-mcp-server",
                }
            ],
            "images": [],
            "custom_details": {
                "description": "This is a test change event sent via the Events API v2",
                "environment": "development",
                "test": True,
            },
            "type": "change_event",
        }

        cls.sample_change_events_list_response = [
            {
                "id": "01G6B73PTIFH786FXPLPEKWG5I",
                "summary": "Test change event from MCP server",
                "timestamp": "2025-11-24T20:45:55Z",
                "services": [cls.sample_service],
                "integration": cls.sample_integration,
                "routing_key": "bc0913066d5d4208c09f71ba1f030a03",
                "source": "mcp-server-test",
                "links": [],
                "images": [],
                "custom_details": {"description": "Test event 1"},
                "type": "change_event",
            },
            {
                "id": "01G6B73PTIFH786FXPLPEKWG5J",
                "summary": "Database deployment to prod",
                "timestamp": "2025-11-24T21:00:00Z",
                "services": [cls.sample_service],
                "integration": cls.sample_integration,
                "routing_key": "bc0913066d5d4208c09f71ba1f030a03",
                "source": "prod-db-01",
                "links": [],
                "images": [],
                "custom_details": {"version": "2.1.0", "deployment_time": "5m"},
                "type": "change_event",
            },
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_no_filters(self, mock_get_client, mock_paginate):
        """Test listing change events without any filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_change_events_list_response

        query = ChangeEventQuery()
        result = list_change_events(query)

        # Verify paginate call
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="change_events", params=query.to_params(), maximum_records=DEFAULT_PAGINATION_LIMIT
        )

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], ChangeEvent)
        self.assertIsInstance(result.response[1], ChangeEvent)
        self.assertEqual(result.response[0].id, "01G6B73PTIFH786FXPLPEKWG5I")
        self.assertEqual(result.response[1].id, "01G6B73PTIFH786FXPLPEKWG5J")
        self.assertEqual(result.response[0].summary, "Test change event from MCP server")
        self.assertEqual(result.response[1].summary, "Database deployment to prod")

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_with_team_filter(self, mock_get_client, mock_paginate):
        """Test listing change events with team filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_change_events_list_response[0]]

        query = ChangeEventQuery(team_ids=["TEAM123"])
        result = list_change_events(query)

        # Verify paginate call
        expected_params = {"team_ids[]": ["TEAM123"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="change_events", params=expected_params, maximum_records=DEFAULT_PAGINATION_LIMIT
        )

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].summary, "Test change event from MCP server")

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_with_date_range(self, mock_get_client, mock_paginate):
        """Test listing change events with date range filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_change_events_list_response

        since = datetime.now() - timedelta(days=7)
        until = datetime.now()
        query = ChangeEventQuery(since=since, until=until)
        result = list_change_events(query)

        # Verify paginate call
        expected_params = {
            "since": since.isoformat(),
            "until": until.isoformat(),
            "limit": DEFAULT_PAGINATION_LIMIT,
        }
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="change_events", params=expected_params, maximum_records=DEFAULT_PAGINATION_LIMIT
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_with_integration_filter(self, mock_get_client, mock_paginate):
        """Test listing change events with integration filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_change_events_list_response[1]]

        query = ChangeEventQuery(integration_ids=["P0Z3BFB"])
        result = list_change_events(query)

        # Verify paginate call
        expected_params = {"integration_ids[]": ["P0Z3BFB"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="change_events", params=expected_params, maximum_records=DEFAULT_PAGINATION_LIMIT
        )

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_with_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing change events with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_change_events_list_response

        query = ChangeEventQuery(limit=50)
        result = list_change_events(query)

        # Verify paginate call
        expected_params = {"limit": 50}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="change_events", params=expected_params, maximum_records=50
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_with_offset_and_total(self, mock_get_client, mock_paginate):
        """Test listing change events with offset and total parameters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_change_events_list_response[1]]

        query = ChangeEventQuery(limit=25, offset=10, total=True)
        result = list_change_events(query)

        # Verify paginate call
        expected_params = {"limit": 25, "offset": 10, "total": True}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="change_events", params=expected_params, maximum_records=25
        )

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_change_events_empty_response(self, mock_get_client, mock_paginate):
        """Test listing change events when paginate returns empty list."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        query = ChangeEventQuery()
        result = list_change_events(query)

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_get_change_event_success_wrapped_response(self, mock_get_client):
        """Test successful retrieval of a specific change event with wrapped response."""
        mock_get_client.return_value = self.mock_client
        # API response with change_event wrapped in 'change_event' key
        wrapped_response = {"change_event": self.sample_change_event_response}
        self.mock_client.rget.return_value = wrapped_response

        result = get_change_event("01G6B73PTIFH786FXPLPEKWG5I")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/change_events/01G6B73PTIFH786FXPLPEKWG5I")

        # Verify result
        self.assertIsInstance(result, ChangeEvent)
        self.assertEqual(result.id, "01G6B73PTIFH786FXPLPEKWG5I")
        self.assertEqual(result.summary, "Test change event from MCP server")
        self.assertEqual(result.source, "mcp-server-test")
        self.assertEqual(result.routing_key, "bc0913066d5d4208c09f71ba1f030a03")
        self.assertIsInstance(result.services[0], ServiceReference)
        self.assertEqual(result.services[0].id, "P43PBXB")
        self.assertIsInstance(result.integration, IntegrationReference)
        self.assertEqual(result.integration.id, "P0Z3BFB")
        self.assertEqual(len(result.links), 1)
        self.assertEqual(result.custom_details["description"], "This is a test change event sent via the Events API v2")
        self.assertEqual(result.type, "change_event")

    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_get_change_event_success_direct_response(self, mock_get_client):
        """Test successful retrieval of a specific change event with direct response."""
        mock_get_client.return_value = self.mock_client
        # API response directly as change event object
        self.mock_client.rget.return_value = self.sample_change_event_response

        result = get_change_event("01G6B73PTIFH786FXPLPEKWG5I")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/change_events/01G6B73PTIFH786FXPLPEKWG5I")

        # Verify result
        self.assertIsInstance(result, ChangeEvent)
        self.assertEqual(result.id, "01G6B73PTIFH786FXPLPEKWG5I")
        self.assertEqual(result.summary, "Test change event from MCP server")

    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_get_change_event_client_error(self, mock_get_client):
        """Test get_change_event when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_change_event("01G6B73PTIFH786FXPLPEKWG5I")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/change_events/01G6B73PTIFH786FXPLPEKWG5I")

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_service_change_events_success(self, mock_get_client, mock_paginate):
        """Test listing change events for a specific service."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_change_events_list_response

        query = ChangeEventQuery(limit=20)
        result = list_service_change_events("P43PBXB", query)

        # Verify paginate call
        expected_params = {"limit": 20}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="services/P43PBXB/change_events", params=expected_params, maximum_records=20
        )

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], ChangeEvent)
        self.assertEqual(result.response[0].id, "01G6B73PTIFH786FXPLPEKWG5I")

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_service_change_events_with_date_range(self, mock_get_client, mock_paginate):
        """Test listing service change events with date range."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_change_events_list_response[0]]

        since = datetime.now() - timedelta(hours=24)
        query = ChangeEventQuery(since=since, limit=10)
        result = list_service_change_events("P43PBXB", query)

        # Verify paginate call
        expected_params = {"since": since.isoformat(), "limit": 10}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="services/P43PBXB/change_events", params=expected_params, maximum_records=10
        )

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_incident_change_events_success(self, mock_get_client, mock_paginate):
        """Test listing change events related to an incident."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_change_events_list_response

        result = list_incident_change_events("INC123", limit=10)

        # Verify paginate call
        expected_params = {"limit": 10}
        mock_paginate.assert_called_once_with(
            client=self.mock_client,
            entity="incidents/INC123/related_change_events",
            params=expected_params,
            maximum_records=10,
        )

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], ChangeEvent)

    @patch("pagerduty_mcp.tools.change_events.paginate")
    @patch("pagerduty_mcp.tools.change_events.get_client")
    def test_list_incident_change_events_no_limit(self, mock_get_client, mock_paginate):
        """Test listing incident change events without limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_change_events_list_response

        result = list_incident_change_events("INC123")

        # Verify paginate call with default limit
        expected_params = {}
        mock_paginate.assert_called_once_with(
            client=self.mock_client,
            entity="incidents/INC123/related_change_events",
            params=expected_params,
            maximum_records=100,
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    def test_change_event_query_to_params_all_fields(self):
        """Test ChangeEventQuery.to_params() with all fields set."""
        since = datetime(2025, 11, 20, 10, 0, 0)
        until = datetime(2025, 11, 24, 10, 0, 0)
        query = ChangeEventQuery(
            limit=50, offset=10, total=True, team_ids=["TEAM1", "TEAM2"], integration_ids=["INT1"], since=since, until=until
        )

        params = query.to_params()

        expected_params = {
            "limit": 50,
            "offset": 10,
            "total": True,
            "team_ids[]": ["TEAM1", "TEAM2"],
            "integration_ids[]": ["INT1"],
            "since": since.isoformat(),
            "until": until.isoformat(),
        }
        self.assertEqual(params, expected_params)

    def test_change_event_query_to_params_partial_fields(self):
        """Test ChangeEventQuery.to_params() with only some fields set."""
        query = ChangeEventQuery(limit=25, team_ids=["TEAM1"])

        params = query.to_params()

        expected_params = {"limit": 25, "team_ids[]": ["TEAM1"]}
        self.assertEqual(params, expected_params)

    def test_change_event_query_to_params_empty(self):
        """Test ChangeEventQuery.to_params() with no fields set."""
        query = ChangeEventQuery()

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_change_event_query_validation_limit_bounds(self):
        """Test ChangeEventQuery limit validation within bounds."""
        # Test minimum limit
        query = ChangeEventQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = ChangeEventQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = ChangeEventQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)

    def test_change_event_query_validation_offset(self):
        """Test ChangeEventQuery offset validation."""
        # Test zero offset
        query = ChangeEventQuery(offset=0)
        self.assertEqual(query.offset, 0)

        # Test positive offset
        query = ChangeEventQuery(offset=100)
        self.assertEqual(query.offset, 100)

    def test_change_event_model_computed_type(self):
        """Test ChangeEvent model computed type property."""
        change_event = ChangeEvent(
            id="TEST123",
            summary="Test change event",
            timestamp=datetime.now(),
            services=[],
            integration=None,
            routing_key="test-key",
            source="test-source",
            custom_details={},
        )

        self.assertEqual(change_event.type, "change_event")


if __name__ == "__main__":
    unittest.main()
