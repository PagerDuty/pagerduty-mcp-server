import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.event_orchestrations import (
    EventOrchestration,
    EventOrchestrationQuery,
    EventOrchestrationRouter,
)
from pagerduty_mcp.tools.event_orchestrations import (
    get_event_orchestration,
    get_event_orchestration_router,
    list_event_orchestrations,
)


class TestEventOrchestrationTools(unittest.TestCase):
    """Test cases for event orchestration tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_team = {
            "id": "PQYP5MN",
            "type": "team_reference",
            "self": "https://api.pagerduty.com/teams/PQYP5MN",
            "summary": "Engineering Team",
        }

        cls.sample_user = {
            "id": "P8B9WR8",
            "self": "https://api.pagerduty.com/users/P8B9WR8",
            "type": "user_reference",
            "summary": "John Doe",
        }

        cls.sample_integration = {
            "id": "9c5ff030-12da-4204-a067-25ee61a8df6c",
            "label": "Shopping Cart Orchestration Default Integration",
            "parameters": {"routing_key": "R028DIE06SNKNO6V5ACSLRV7Y0TUVG7T", "type": "global"},
        }

        cls.sample_orchestration_response = {
            "id": "b02e973d-9620-4e0a-9edc-00fedf7d4694",
            "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694",
            "name": "Shopping Cart Orchestration",
            "description": "Send shopping cart alerts to the right services",
            "team": cls.sample_team,
            "integrations": [cls.sample_integration],
            "routes": 0,
            "created_at": "2021-11-18T16:42:01Z",
            "created_by": cls.sample_user,
            "updated_at": "2021-11-18T16:42:01Z",
            "updated_by": cls.sample_user,
            "version": "9co0z4b152oICsoV91_PW2.ww8ip_xap",
        }

        cls.sample_orchestrations_list_response = [
            {
                "id": "b02e973d-9620-4e0a-9edc-00fedf7d4694",
                "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694",
                "name": "Shopping Cart Orchestration",
                "description": "Send shopping cart alerts to the right services",
                "team": cls.sample_team,
                "routes": 0,
                "created_at": "2021-11-18T16:42:01Z",
                "created_by": cls.sample_user,
                "updated_at": "2021-11-18T16:42:01Z",
                "updated_by": cls.sample_user,
                "version": "9co0z4b152oICsoV91_PW2.ww8ip_xap",
            },
            {
                "id": "a01e863d-8520-3e0a-8abc-00abcd1d2345",
                "self": "https://api.pagerduty.com/event_orchestrations/a01e863d-8520-3e0a-8abc-00abcd1d2345",
                "name": "Database Alerts Orchestration",
                "description": "Route database alerts to appropriate teams",
                "team": cls.sample_team,
                "routes": 2,
                "created_at": "2021-10-15T10:30:00Z",
                "created_by": cls.sample_user,
                "updated_at": "2021-10-15T10:30:00Z",
                "updated_by": cls.sample_user,
                "version": "abc123def456ghi789jkl012mno345pqr",
            },
        ]

        cls.sample_router_response = {
            "orchestration_path": {
                "type": "router",
                "parent": {
                    "id": "b02e973d-9620-4e0a-9edc-00fedf7d4694",
                    "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694",
                    "type": "event_orchestration_reference",
                },
                "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router",
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            {
                                "label": "Events relating to our relational database",
                                "id": "1c26698b",
                                "conditions": [
                                    {"expression": "event.summary matches part 'database'"},
                                    {"expression": "event.source matches regex 'db[0-9]+-server'"},
                                ],
                                "actions": {"route_to": "PB31XBA"},
                            },
                            {
                                "label": "Events relating to our www app server",
                                "id": "d9801904",
                                "conditions": [{"expression": "event.summary matches part 'www'"}],
                                "actions": {"route_to": "PC2D9ML"},
                            },
                        ],
                    }
                ],
                "catch_all": {"actions": {"route_to": "unrouted"}},
                "created_at": "2021-11-18T16:42:01Z",
                "created_by": cls.sample_user,
                "updated_at": "2021-11-18T16:42:01Z",
                "updated_by": cls.sample_user,
                "version": "9co0z4b152oICsoV91_PW2.ww8ip_xap",
            }
        }

    def test_event_orchestration_query_model(self):
        """Test EventOrchestrationQuery model functionality."""
        # Test default values
        query = EventOrchestrationQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)
        self.assertEqual(query.offset, None)
        self.assertEqual(query.sort_by, "name:asc")

        # Test custom values
        query = EventOrchestrationQuery(limit=50, offset=10, sort_by="created_at:desc")
        self.assertEqual(query.limit, 50)
        self.assertEqual(query.offset, 10)
        self.assertEqual(query.sort_by, "created_at:desc")

        # Test to_params method
        params = query.to_params()
        expected = {"limit": 50, "offset": 10, "sort_by": "created_at:desc"}
        self.assertEqual(params, expected)

    def test_event_orchestration_query_validation(self):
        """Test EventOrchestrationQuery validation."""
        # Test limit validation - minimum
        with self.assertRaises(ValueError):
            EventOrchestrationQuery(limit=0)

        # Test limit validation - maximum
        with self.assertRaises(ValueError):
            EventOrchestrationQuery(limit=MAXIMUM_PAGINATION_LIMIT + 1)

        # Test negative offset
        with self.assertRaises(ValueError):
            EventOrchestrationQuery(offset=-1)

        # Test invalid sort_by
        with self.assertRaises(ValueError):
            EventOrchestrationQuery(sort_by="invalid_sort")

    def test_event_orchestration_query_to_params_empty(self):
        """Test to_params with default values."""
        query = EventOrchestrationQuery(limit=None, offset=None, sort_by=None)
        params = query.to_params()
        self.assertEqual(params, {})

    @patch("pagerduty_mcp.tools.event_orchestrations.paginate")
    def test_list_event_orchestrations_success(self, mock_paginate):
        """Test successful list_event_orchestrations call."""
        # Mock the paginate response
        mock_paginate.return_value = self.sample_orchestrations_list_response

        # Create query and call function
        query = EventOrchestrationQuery(limit=25, sort_by="name:asc")
        result = list_event_orchestrations(query)

        # Assert paginate was called correctly
        mock_paginate.assert_called_once()
        call_args = mock_paginate.call_args
        self.assertEqual(call_args[1]["entity"], "event_orchestrations")
        expected_params = {"limit": 25, "sort_by": "name:asc"}
        self.assertEqual(call_args[1]["params"], expected_params)

        # Assert result structure
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], EventOrchestration)
        self.assertEqual(result.response[0].id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(result.response[0].name, "Shopping Cart Orchestration")

    @patch("pagerduty_mcp.tools.event_orchestrations.paginate")
    def test_list_event_orchestrations_empty_response(self, mock_paginate):
        """Test list_event_orchestrations with empty response."""
        mock_paginate.return_value = []

        query = EventOrchestrationQuery()
        result = list_event_orchestrations(query)

        self.assertEqual(len(result.response), 0)
        mock_paginate.assert_called_once()

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_success(self, mock_get_client):
        """Test successful get_event_orchestration call."""
        # Mock the client response
        mock_client = MagicMock()
        mock_client.rget.return_value = {"orchestration": self.sample_orchestration_response}
        mock_get_client.return_value = mock_client

        # Call function
        result = get_event_orchestration("b02e973d-9620-4e0a-9edc-00fedf7d4694")

        # Assert client was called correctly
        mock_client.rget.assert_called_once_with("/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694")

        # Assert result
        self.assertIsInstance(result, EventOrchestration)
        self.assertEqual(result.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(result.name, "Shopping Cart Orchestration")
        self.assertEqual(result.description, "Send shopping cart alerts to the right services")
        self.assertEqual(result.routes, 0)
        self.assertEqual(result.team.id, "PQYP5MN")
        self.assertEqual(len(result.integrations), 1)

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_direct_response(self, mock_get_client):
        """Test get_event_orchestration with direct response (no wrapper)."""
        # Mock the client response without wrapper
        mock_client = MagicMock()
        mock_client.rget.return_value = self.sample_orchestration_response
        mock_get_client.return_value = mock_client

        # Call function
        result = get_event_orchestration("b02e973d-9620-4e0a-9edc-00fedf7d4694")

        # Assert result
        self.assertIsInstance(result, EventOrchestration)
        self.assertEqual(result.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(result.name, "Shopping Cart Orchestration")

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_router_success(self, mock_get_client):
        """Test successful get_event_orchestration_router call."""
        # Mock the client response
        mock_client = MagicMock()
        mock_client.rget.return_value = self.sample_router_response
        mock_get_client.return_value = mock_client

        # Call function
        result = get_event_orchestration_router("b02e973d-9620-4e0a-9edc-00fedf7d4694")

        # Assert client was called correctly
        mock_client.rget.assert_called_once_with("/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router")

        # Assert result
        self.assertIsInstance(result, EventOrchestrationRouter)
        orchestration_path = result.orchestration_path
        self.assertEqual(orchestration_path.type, "router")
        self.assertEqual(orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(len(orchestration_path.sets), 1)
        self.assertEqual(len(orchestration_path.sets[0].rules), 2)

        # Test first rule
        first_rule = orchestration_path.sets[0].rules[0]
        self.assertEqual(first_rule.id, "1c26698b")
        self.assertEqual(first_rule.label, "Events relating to our relational database")
        self.assertEqual(len(first_rule.conditions), 2)
        self.assertEqual(first_rule.actions.route_to, "PB31XBA")

        # Test catch_all
        self.assertEqual(orchestration_path.catch_all.actions.route_to, "unrouted")

    def test_event_orchestration_model_validation(self):
        """Test EventOrchestration model validation and properties."""
        orchestration = EventOrchestration(**self.sample_orchestration_response)

        # Test basic properties
        self.assertEqual(orchestration.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(orchestration.name, "Shopping Cart Orchestration")
        self.assertEqual(orchestration.description, "Send shopping cart alerts to the right services")
        self.assertEqual(orchestration.routes, 0)
        self.assertEqual(orchestration.type, "event_orchestration")

        # Test team reference
        self.assertEqual(orchestration.team.id, "PQYP5MN")
        self.assertEqual(orchestration.team.type, "team_reference")

        # Test integration
        self.assertEqual(len(orchestration.integrations), 1)
        integration = orchestration.integrations[0]
        self.assertEqual(integration.id, "9c5ff030-12da-4204-a067-25ee61a8df6c")
        self.assertEqual(integration.label, "Shopping Cart Orchestration Default Integration")

        # Test datetime parsing
        self.assertIsInstance(orchestration.created_at, datetime)
        self.assertIsInstance(orchestration.updated_at, datetime)

        # Test user references
        self.assertEqual(orchestration.created_by.id, "P8B9WR8")
        self.assertEqual(orchestration.updated_by.id, "P8B9WR8")

    def test_event_orchestration_router_model_validation(self):
        """Test EventOrchestrationRouter model validation."""
        router = EventOrchestrationRouter(**self.sample_router_response)

        # Test orchestration path
        orchestration_path = router.orchestration_path
        self.assertEqual(orchestration_path.type, "router")

        # Test parent reference
        parent = orchestration_path.parent
        self.assertEqual(parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(parent.type, "event_orchestration_reference")

        # Test rule sets
        self.assertEqual(len(orchestration_path.sets), 1)
        rule_set = orchestration_path.sets[0]
        self.assertEqual(rule_set.id, "start")
        self.assertEqual(len(rule_set.rules), 2)

        # Test individual rules
        database_rule = rule_set.rules[0]
        self.assertEqual(database_rule.id, "1c26698b")
        self.assertEqual(database_rule.label, "Events relating to our relational database")
        self.assertEqual(len(database_rule.conditions), 2)
        self.assertEqual(database_rule.actions.route_to, "PB31XBA")

        www_rule = rule_set.rules[1]
        self.assertEqual(www_rule.id, "d9801904")
        self.assertEqual(www_rule.label, "Events relating to our www app server")
        self.assertEqual(len(www_rule.conditions), 1)
        self.assertEqual(www_rule.actions.route_to, "PC2D9ML")

        # Test catch_all
        catch_all = orchestration_path.catch_all
        self.assertEqual(catch_all.actions.route_to, "unrouted")

    def test_event_orchestration_model_with_none_values(self):
        """Test EventOrchestration model handles None values correctly."""
        # Test data with None values for optional fields
        test_data = {
            "id": "test-orchestration-id",
            "self": "https://api.pagerduty.com/event_orchestrations/test-orchestration-id",
            "name": "Test Orchestration",
            "routes": 0,
            "created_at": "2025-04-20T00:00:00Z",
            "updated_at": "2025-04-20T00:00:00Z",
            # These fields are None in some API responses
            "description": None,
            "team": None,
            "integrations": None,
            "created_by": None,
            "updated_by": None,
            "version": None,
        }

        orchestration = EventOrchestration.model_validate(test_data)

        self.assertEqual(orchestration.id, "test-orchestration-id")
        self.assertEqual(orchestration.name, "Test Orchestration")
        self.assertIsNone(orchestration.description)
        self.assertIsNone(orchestration.team)
        self.assertIsNone(orchestration.integrations)
        self.assertIsNone(orchestration.created_by)
        self.assertIsNone(orchestration.updated_by)
        self.assertIsNone(orchestration.version)
        self.assertEqual(orchestration.type, "event_orchestration")

        # Test datetime fields
        self.assertIsInstance(orchestration.created_at, datetime)
        self.assertIsInstance(orchestration.updated_at, datetime)

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_router_direct_response(self, mock_get_client):
        """Test get_event_orchestration_router handles direct API responses correctly."""
        # API response without orchestration_path wrapper
        direct_router_response = {
            "type": "router",
            "parent": {
                "id": "b02e973d-9620-4e0a-9edc-00fedf7d4694",
                "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694",
                "type": "event_orchestration_reference",
            },
            "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router",
            "sets": [
                {
                    "id": "start",
                    "rules": [
                        {
                            "label": "Database events",
                            "id": "1c26698b",
                            "conditions": [{"expression": "event.summary matches part 'database'"}],
                            "actions": {"route_to": "PB31XBA"},
                        }
                    ],
                }
            ],
            "catch_all": {"actions": {"route_to": "unrouted"}},
            "created_at": "2021-10-15T10:30:00Z",
            "created_by": self.sample_user,
            "updated_at": "2021-10-15T10:30:00Z",
            "updated_by": self.sample_user,
            "version": "abc123def456ghi789jkl012mno345pqr",
        }

        mock_client = MagicMock()
        mock_client.rget.return_value = direct_router_response
        mock_get_client.return_value = mock_client

        result = get_event_orchestration_router("b02e973d-9620-4e0a-9edc-00fedf7d4694")

        # Verify the function wraps the direct response correctly
        self.assertIsInstance(result, EventOrchestrationRouter)
        self.assertEqual(result.orchestration_path.type, "router")
        self.assertEqual(result.orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(len(result.orchestration_path.sets), 1)
        self.assertEqual(result.orchestration_path.catch_all.actions.route_to, "unrouted")

    def test_event_orchestration_router_from_api_response_wrapped(self):
        """Test EventOrchestrationRouter.from_api_response with wrapped response."""
        wrapped_response = self.sample_router_response
        router = EventOrchestrationRouter.from_api_response(wrapped_response)

        self.assertIsInstance(router, EventOrchestrationRouter)
        self.assertEqual(router.orchestration_path.type, "router")
        self.assertEqual(router.orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")

    def test_event_orchestration_router_from_api_response_direct(self):
        """Test EventOrchestrationRouter.from_api_response with direct response."""
        direct_response = self.sample_router_response["orchestration_path"]
        router = EventOrchestrationRouter.from_api_response(direct_response)

        self.assertIsInstance(router, EventOrchestrationRouter)
        self.assertEqual(router.orchestration_path.type, "router")
        self.assertEqual(router.orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")

    def test_event_orchestration_router_with_empty_sets(self):
        """Test EventOrchestrationRouter model handles empty rule sets correctly."""
        # Test data with empty sets (orchestration with no rules configured)
        test_data = {
            "orchestration_path": {
                "type": "router",
                "parent": {
                    "id": "empty-orchestration-id",
                    "self": "https://api.pagerduty.com/event_orchestrations/empty-orchestration-id",
                    "type": "event_orchestration_reference",
                },
                "self": "https://api.pagerduty.com/event_orchestrations/empty-orchestration-id/router",
                "sets": [],  # Empty rule sets
                "catch_all": {"actions": {"route_to": "unrouted"}},
                "created_at": "2025-04-20T00:00:00Z",
                "updated_at": "2025-04-20T00:00:00Z",
                "version": "empty-version",
            }
        }

        router = EventOrchestrationRouter.model_validate(test_data)

        self.assertEqual(router.orchestration_path.type, "router")
        self.assertEqual(router.orchestration_path.parent.id, "empty-orchestration-id")
        self.assertEqual(len(router.orchestration_path.sets), 0)  # Should handle empty sets
        self.assertEqual(router.orchestration_path.catch_all.actions.route_to, "unrouted")


if __name__ == "__main__":
    unittest.main()
