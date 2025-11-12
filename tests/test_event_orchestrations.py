import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.event_orchestrations import (
    EventOrchestration,
    EventOrchestrationGlobal,
    EventOrchestrationQuery,
    EventOrchestrationRouter,
    EventOrchestrationRouterUpdateRequest,
    EventOrchestrationRuleActions,
    EventOrchestrationRuleCondition,
    EventOrchestrationRuleCreateRequest,
    EventOrchestrationService,
)
from pagerduty_mcp.tools.event_orchestrations import (
    append_event_orchestration_router_rule,
    get_event_orchestration,
    get_event_orchestration_global,
    get_event_orchestration_router,
    get_event_orchestration_service,
    list_event_orchestrations,
    update_event_orchestration_router,
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

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_update_event_orchestration_router_success(self, mock_get_client):
        """Test successful update_event_orchestration_router call."""
        # Mock the client response
        mock_client = MagicMock()
        mock_client.rput.return_value = self.sample_router_response
        mock_get_client.return_value = mock_client

        # Create update request using factory method to exclude readonly fields
        from pagerduty_mcp.models.event_orchestrations import EventOrchestrationPath

        path = EventOrchestrationPath.model_validate(self.sample_router_response["orchestration_path"])
        update_request = EventOrchestrationRouterUpdateRequest.from_path(path)

        # Call function
        result = update_event_orchestration_router("b02e973d-9620-4e0a-9edc-00fedf7d4694", update_request)

        # Assert client was called correctly
        mock_client.rput.assert_called_once_with(
            "/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router", json=update_request.model_dump()
        )

        # Assert result
        self.assertIsInstance(result, EventOrchestrationRouter)
        self.assertEqual(result.orchestration_path.type, "router")
        self.assertEqual(result.orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_update_event_orchestration_router_direct_response(self, mock_get_client):
        """Test update_event_orchestration_router with direct API response (no wrapper)."""
        # Mock the client to return direct response format
        direct_response = self.sample_router_response["orchestration_path"]
        mock_client = MagicMock()
        mock_client.rput.return_value = direct_response
        mock_get_client.return_value = mock_client

        # Create update request using factory method to exclude readonly fields
        from pagerduty_mcp.models.event_orchestrations import EventOrchestrationPath

        path = EventOrchestrationPath.model_validate(direct_response)
        update_request = EventOrchestrationRouterUpdateRequest.from_path(path)

        # Call function
        result = update_event_orchestration_router("b02e973d-9620-4e0a-9edc-00fedf7d4694", update_request)

        # Assert result
        self.assertIsInstance(result, EventOrchestrationRouter)
        self.assertEqual(result.orchestration_path.type, "router")
        self.assertEqual(result.orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_append_event_orchestration_router_rule_success(self, mock_get_client):
        """Test successful append_event_orchestration_router_rule call."""
        # Mock the client responses
        mock_client = MagicMock()

        # Mock GET response (current router config)
        mock_client.rget.return_value = self.sample_router_response

        # Mock PUT response (updated router config with new rule)
        updated_response = {
            "orchestration_path": {
                **self.sample_router_response["orchestration_path"],
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            *self.sample_router_response["orchestration_path"]["sets"][0]["rules"],
                            {
                                "label": "New monitoring rule",
                                "id": "new_rule_id",
                                "conditions": [{"expression": "event.summary matches part 'monitoring'"}],
                                "actions": {"route_to": "NEW_SERVICE"},
                            },
                        ],
                    }
                ],
            }
        }
        mock_client.rput.return_value = updated_response
        mock_get_client.return_value = mock_client

        # Create new rule request
        new_rule = EventOrchestrationRuleCreateRequest(
            label="New monitoring rule",
            conditions=[EventOrchestrationRuleCondition(expression="event.summary matches part 'monitoring'")],
            actions=EventOrchestrationRuleActions(route_to="NEW_SERVICE"),
        )

        # Call function
        result = append_event_orchestration_router_rule("b02e973d-9620-4e0a-9edc-00fedf7d4694", new_rule)

        # Assert GET was called to fetch current config
        mock_client.rget.assert_called_once_with("/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router")

        # Assert PUT was called with updated config
        mock_client.rput.assert_called_once()
        put_call_args = mock_client.rput.call_args
        self.assertEqual(put_call_args[0][0], "/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router")

        # Verify the PUT request contains the new rule
        put_data = put_call_args[1]["json"]  # Access json keyword argument
        self.assertIn("orchestration_path", put_data)
        rules = put_data["orchestration_path"]["sets"][0]["rules"]
        self.assertEqual(len(rules), 3)  # Original 2 + 1 new rule

        # Check the new rule was appended
        new_rule_data = rules[-1]  # Last rule should be the new one
        self.assertEqual(new_rule_data["label"], "New monitoring rule")
        self.assertEqual(new_rule_data["actions"]["route_to"], "NEW_SERVICE")

        # Assert result
        self.assertIsInstance(result, EventOrchestrationRouter)
        self.assertEqual(len(result.orchestration_path.sets[0].rules), 3)

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_append_event_orchestration_router_rule_empty_rules(self, mock_get_client):
        """Test append_event_orchestration_router_rule with empty existing rules."""
        # Create router response with empty rules
        empty_router_response = {
            "orchestration_path": {
                "type": "router",
                "parent": {
                    "id": "b02e973d-9620-4e0a-9edc-00fedf7d4694",
                    "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694",
                    "type": "event_orchestration_reference",
                },
                "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/router",
                "sets": [{"id": "start", "rules": []}],  # No existing rules
                "catch_all": {"actions": {"route_to": "unrouted"}},
                "created_at": "2021-11-18T16:42:01Z",
                "created_by": self.sample_user,
                "updated_at": "2021-11-18T16:42:01Z",
                "updated_by": self.sample_user,
                "version": "9co0z4b152oICsoV91_PW2.ww8ip_xap",
            }
        }

        # Mock the client responses
        mock_client = MagicMock()
        mock_client.rget.return_value = empty_router_response

        # Mock PUT response with the new rule added
        updated_response = {
            "orchestration_path": {
                **empty_router_response["orchestration_path"],
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            {
                                "label": "First rule",
                                "id": "first_rule_id",
                                "conditions": [{"expression": "event.summary matches part 'error'"}],
                                "actions": {"route_to": "ERROR_SERVICE"},
                            }
                        ],
                    }
                ],
            }
        }
        mock_client.rput.return_value = updated_response
        mock_get_client.return_value = mock_client

        # Create new rule request
        new_rule = EventOrchestrationRuleCreateRequest(
            label="First rule",
            conditions=[EventOrchestrationRuleCondition(expression="event.summary matches part 'error'")],
            actions=EventOrchestrationRuleActions(route_to="ERROR_SERVICE"),
        )

        # Call function
        result = append_event_orchestration_router_rule("b02e973d-9620-4e0a-9edc-00fedf7d4694", new_rule)

        # Assert both GET and PUT were called
        mock_client.rget.assert_called_once()
        mock_client.rput.assert_called_once()

        # Verify the result
        self.assertIsInstance(result, EventOrchestrationRouter)
        self.assertEqual(len(result.orchestration_path.sets[0].rules), 1)
        self.assertEqual(result.orchestration_path.sets[0].rules[0].label, "First rule")

    @patch("pagerduty_mcp.tools.event_orchestrations.get_event_orchestration_router")
    def test_append_event_orchestration_router_rule_invalid_config(self, mock_get_router):
        """Test append_event_orchestration_router_rule with invalid router configuration."""
        # Mock router with no orchestration_path
        invalid_router = EventOrchestrationRouter(orchestration_path=None)
        mock_get_router.return_value = invalid_router

        # Create new rule request
        new_rule = EventOrchestrationRuleCreateRequest(
            label="Test rule",
            conditions=[EventOrchestrationRuleCondition(expression="event.summary matches part 'test'")],
            actions=EventOrchestrationRuleActions(route_to="TEST_SERVICE"),
        )

        # Should raise ValueError for invalid configuration
        with self.assertRaises(ValueError) as context:
            append_event_orchestration_router_rule("invalid-orchestration-id", new_rule)

        self.assertIn("has no valid router configuration", str(context.exception))

    def test_event_orchestration_router_update_request_model(self):
        """Test EventOrchestrationRouterUpdateRequest model validation."""
        from pagerduty_mcp.models.event_orchestrations import EventOrchestrationPath

        # Create an EventOrchestrationPath from the sample data
        path = EventOrchestrationPath.model_validate(self.sample_router_response["orchestration_path"])

        # Use the factory method to create the update request, which excludes readonly fields
        update_request = EventOrchestrationRouterUpdateRequest.from_path(path)

        self.assertEqual(update_request.orchestration_path.type, "router")
        self.assertEqual(len(update_request.orchestration_path.sets), 1)

        # Verify that readonly fields are excluded
        path_dict = update_request.orchestration_path.model_dump()
        self.assertNotIn("created_at", path_dict)
        self.assertNotIn("updated_at", path_dict)
        self.assertNotIn("version", path_dict)
        self.assertNotIn("parent", path_dict)  # parent is also excluded from update requests

    def test_event_orchestration_rule_create_request_model(self):
        """Test EventOrchestrationRuleCreateRequest model validation."""
        rule_data = {
            "label": "Test rule",
            "conditions": [{"expression": "event.summary matches part 'test'"}],
            "actions": {"route_to": "TEST_SERVICE"},
            "disabled": False,
        }

        rule_request = EventOrchestrationRuleCreateRequest.model_validate(rule_data)

        self.assertEqual(rule_request.label, "Test rule")
        self.assertEqual(len(rule_request.conditions), 1)
        self.assertEqual(rule_request.conditions[0].expression, "event.summary matches part 'test'")
        self.assertEqual(rule_request.actions.route_to, "TEST_SERVICE")
        self.assertEqual(rule_request.disabled, False)

    def test_event_orchestration_rule_create_request_minimal(self):
        """Test EventOrchestrationRuleCreateRequest with minimal required fields."""
        rule_data = {
            "conditions": [{"expression": "event.summary matches part 'minimal'"}],
            "actions": {"route_to": "MINIMAL_SERVICE"},
        }

        rule_request = EventOrchestrationRuleCreateRequest.model_validate(rule_data)

        self.assertIsNone(rule_request.label)  # Optional field
        self.assertEqual(len(rule_request.conditions), 1)
        self.assertEqual(rule_request.actions.route_to, "MINIMAL_SERVICE")
        self.assertEqual(rule_request.disabled, False)  # Default value

    def test_serialization_fix_excludes_readonly_fields(self):
        """Test that the fix properly excludes readonly fields from update requests.

        This test verifies that the EventOrchestrationRouterUpdateRequest.from_path()
        factory method excludes readonly fields that would cause JSON serialization errors.
        """
        import json

        from pagerduty_mcp.models.event_orchestrations import (
            EventOrchestrationPath,
            EventOrchestrationRouterUpdateRequest,
        )

        # Create orchestration path data similar to what comes from the API
        # This includes readonly datetime fields
        orchestration_path_data = {
            "type": "router",
            "parent": {
                "id": "test-orchestration-id",
                "type": "event_orchestration_reference",
                "self": "https://api.pagerduty.com/event_orchestrations/test-orchestration-id",
            },
            "self": "https://api.pagerduty.com/event_orchestrations/test-orchestration-id/router",
            "sets": [
                {
                    "id": "start",
                    "rules": [
                        {
                            "id": "rule_id_1",
                            "label": "Test rule",
                            "conditions": [{"expression": "event.summary matches part 'test'"}],
                            "actions": {"route_to": "TEST_SERVICE"},
                            "disabled": False,
                        }
                    ],
                }
            ],
            "catch_all": {"actions": {"route_to": "unrouted"}},
            # These readonly fields would cause JSON serialization errors if included
            "created_at": "2021-11-18T16:42:01Z",
            "created_by": self.sample_user,
            "updated_at": "2021-11-18T16:42:01Z",
            "updated_by": self.sample_user,
            "version": "test-version",
        }

        # Create full EventOrchestrationPath (as would come from API)
        path = EventOrchestrationPath.model_validate(orchestration_path_data)

        # Create update request using factory method that excludes readonly fields
        update_request = EventOrchestrationRouterUpdateRequest.from_path(path)

        # Serialize to dict (what happens in update_event_orchestration_router)
        serialized_data = update_request.model_dump()

        # The serialized data should NOT contain readonly fields
        path_data = serialized_data["orchestration_path"]
        self.assertNotIn("created_at", path_data)
        self.assertNotIn("updated_at", path_data)
        self.assertNotIn("version", path_data)
        self.assertNotIn("parent", path_data)
        self.assertNotIn("self", path_data)

        # JSON serialization should now work without errors
        json_data = json.dumps(serialized_data)
        self.assertIsInstance(json_data, str)

        # Verify the essential fields are still present
        self.assertEqual(path_data["type"], "router")
        self.assertIn("sets", path_data)
        self.assertIn("catch_all", path_data)

    def test_mixed_rule_types_validation_behavior(self):
        """Test behavior when mixing EventOrchestrationRule objects with plain dicts.

        This demonstrates what happens in append_event_orchestration_router_rule when it
        mixes EventOrchestrationRule objects with plain dicts - Pydantic handles validation
        but it can cause issues during serialization.
        """
        from pagerduty_mcp.models.event_orchestrations import EventOrchestrationRule, EventOrchestrationRuleSet

        # Create existing rule as an EventOrchestrationRule object
        existing_rule = EventOrchestrationRule(
            id="existing_rule_id",
            label="Existing rule",
            conditions=[EventOrchestrationRuleCondition(expression="event.summary matches part 'existing'")],
            actions=EventOrchestrationRuleActions(route_to="EXISTING_SERVICE"),
            disabled=False,
        )

        # Create new rule as a plain dict (what append_event_orchestration_router_rule currently does)
        new_rule_dict = {
            "id": "new_rule_id",  # Add required id field
            "label": "New rule as dict",
            "conditions": [{"expression": "event.summary matches part 'new'"}],
            "actions": {"route_to": "NEW_SERVICE"},
            "disabled": False,
        }

        # Create rule set with mixed types
        mixed_rules = [existing_rule, new_rule_dict]

        # This should work, but may cause serialization inconsistencies
        rule_set = EventOrchestrationRuleSet(id="start", rules=mixed_rules)

        # Validate that the rule set was created
        self.assertEqual(len(rule_set.rules), 2)

        # Both rules should now be EventOrchestrationRule objects after validation
        self.assertIsInstance(rule_set.rules[0], EventOrchestrationRule)
        self.assertIsInstance(rule_set.rules[1], EventOrchestrationRule)

        # But the original issue is that in append_event_orchestration_router_rule,
        # we're mixing objects and dicts before model validation

    # Tests for Service Orchestration

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_service_success(self, mock_get_client):
        """Test successful get_event_orchestration_service call with wrapped response."""
        sample_service_orchestration_response = {
            "orchestration_path": {
                "type": "service",
                "parent": {
                    "id": "PC2D9ML",
                    "self": "https://api.pagerduty.com/service/PC2D9ML",
                    "type": "service_reference",
                },
                "self": "https://api.pagerduty.com/event_orchestrations/service/PC2D9ML",
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            {
                                "label": "Always apply some consistent event transformations",
                                "id": "c91f72f3",
                                "conditions": [],
                                "actions": {
                                    "variables": [
                                        {
                                            "name": "hostname",
                                            "path": "event.component",
                                            "value": "hostname: (.*)",
                                            "type": "regex",
                                        }
                                    ],
                                    "route_to": "step-two",
                                },
                            }
                        ],
                    }
                ],
                "catch_all": {"actions": {"suppress": True}},
                "created_at": "2021-11-18T16:42:01Z",
                "created_by": self.sample_user,
                "updated_at": "2021-11-18T16:42:01Z",
                "updated_by": self.sample_user,
                "version": "rn1Mja13T1HBdmPChqFilSQXUW2fWXM_",
            }
        }

        mock_client = MagicMock()
        mock_client.jget.return_value = sample_service_orchestration_response
        mock_get_client.return_value = mock_client

        result = get_event_orchestration_service("PC2D9ML")

        mock_client.jget.assert_called_once_with("/event_orchestrations/services/PC2D9ML")

        self.assertIsInstance(result, EventOrchestrationService)
        self.assertIsNotNone(result.orchestration_path)
        self.assertEqual(result.orchestration_path.type, "service")
        self.assertEqual(result.orchestration_path.parent.id, "PC2D9ML")
        self.assertEqual(result.orchestration_path.parent.type, "service_reference")
        self.assertEqual(len(result.orchestration_path.sets), 1)
        self.assertEqual(result.orchestration_path.sets[0].id, "start")

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_service_direct_response(self, mock_get_client):
        """Test get_event_orchestration_service with direct response (no wrapper)."""
        sample_direct_response = {
            "type": "service",
            "parent": {
                "id": "PC2D9ML",
                "self": "https://api.pagerduty.com/service/PC2D9ML",
                "type": "service_reference",
            },
            "self": "https://api.pagerduty.com/event_orchestrations/service/PC2D9ML",
            "sets": [
                {
                    "id": "start",
                    "rules": [
                        {
                            "label": "Test rule",
                            "id": "test123",
                            "conditions": [],
                            "actions": {"suppress": False},
                        }
                    ],
                }
            ],
            "catch_all": {"actions": {"suppress": True}},
            "created_at": "2021-11-18T16:42:01Z",
            "created_by": self.sample_user,
            "updated_at": "2021-11-18T16:42:01Z",
            "updated_by": self.sample_user,
            "version": "version123",
        }

        mock_client = MagicMock()
        mock_client.jget.return_value = sample_direct_response
        mock_get_client.return_value = mock_client

        result = get_event_orchestration_service("PC2D9ML")

        self.assertIsInstance(result, EventOrchestrationService)
        self.assertEqual(result.orchestration_path.type, "service")
        self.assertEqual(result.orchestration_path.parent.id, "PC2D9ML")

    def test_event_orchestration_service_model_validation(self):
        """Test EventOrchestrationService model validation."""
        test_data = {
            "orchestration_path": {
                "type": "service",
                "parent": {
                    "id": "SERVICE123",
                    "self": "https://api.pagerduty.com/service/SERVICE123",
                    "type": "service_reference",
                },
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            {
                                "id": "rule1",
                                "label": "Test Rule",
                                "conditions": [{"expression": "event.severity matches 'critical'"}],
                                "actions": {"priority": "P0IN2KQ", "suppress": False},
                            }
                        ],
                    }
                ],
                "catch_all": {"actions": {"suppress": True}},
            }
        }

        service_orch = EventOrchestrationService.model_validate(test_data)

        self.assertEqual(service_orch.orchestration_path.type, "service")
        self.assertEqual(service_orch.orchestration_path.parent.id, "SERVICE123")
        self.assertEqual(len(service_orch.orchestration_path.sets), 1)
        self.assertEqual(service_orch.orchestration_path.sets[0].rules[0].id, "rule1")

    def test_event_orchestration_service_from_api_response_wrapped(self):
        """Test EventOrchestrationService.from_api_response with wrapped response."""
        wrapped_response = {
            "orchestration_path": {
                "type": "service",
                "parent": {
                    "id": "SERVICE123",
                    "self": "https://api.pagerduty.com/service/SERVICE123",
                    "type": "service_reference",
                },
                "sets": [{"id": "start", "rules": []}],
                "catch_all": {"actions": {"suppress": True}},
            }
        }

        service_orch = EventOrchestrationService.from_api_response(wrapped_response)

        self.assertIsInstance(service_orch, EventOrchestrationService)
        self.assertEqual(service_orch.orchestration_path.type, "service")
        self.assertEqual(service_orch.orchestration_path.parent.id, "SERVICE123")

    def test_event_orchestration_service_from_api_response_direct(self):
        """Test EventOrchestrationService.from_api_response with direct response."""
        direct_response = {
            "type": "service",
            "parent": {
                "id": "SERVICE123",
                "self": "https://api.pagerduty.com/service/SERVICE123",
                "type": "service_reference",
            },
            "sets": [{"id": "start", "rules": []}],
            "catch_all": {"actions": {"suppress": True}},
        }

        service_orch = EventOrchestrationService.from_api_response(direct_response)

        self.assertIsInstance(service_orch, EventOrchestrationService)
        self.assertEqual(service_orch.orchestration_path.type, "service")
        self.assertEqual(service_orch.orchestration_path.parent.id, "SERVICE123")

    # Tests for Global Orchestration

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_global_success(self, mock_get_client):
        """Test successful get_event_orchestration_global call with wrapped response."""
        sample_global_orchestration_response = {
            "orchestration_path": {
                "type": "global",
                "parent": {
                    "id": "b02e973d-9620-4e0a-9edc-00fedf7d4694",
                    "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694",
                    "type": "event_orchestration_reference",
                },
                "self": "https://api.pagerduty.com/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/global",
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            {
                                "label": "Always apply some consistent event transformations",
                                "id": "c91f72f3",
                                "conditions": [],
                                "actions": {
                                    "variables": [
                                        {
                                            "name": "hostname",
                                            "path": "event.component",
                                            "value": "hostname: (.*)",
                                            "type": "regex",
                                        }
                                    ],
                                    "route_to": "step-two",
                                },
                            },
                            {
                                "label": "Drop all events from the very-noisy monitoring tool",
                                "id": "1f6d9a33",
                                "conditions": [{"expression": "event.source matches part 'very-noisy'"}],
                                "actions": {"drop_event": True},
                            },
                        ],
                    }
                ],
                "catch_all": {"actions": {"suppress": True}},
                "created_at": "2021-11-18T16:42:01Z",
                "created_by": self.sample_user,
                "updated_at": "2021-11-18T16:42:01Z",
                "updated_by": self.sample_user,
                "version": "rn1Mja13T1HBdmPChqFilSQXUW2fWXM_",
            }
        }

        mock_client = MagicMock()
        mock_client.rget.return_value = sample_global_orchestration_response
        mock_get_client.return_value = mock_client

        result = get_event_orchestration_global("b02e973d-9620-4e0a-9edc-00fedf7d4694")

        mock_client.rget.assert_called_once_with("/event_orchestrations/b02e973d-9620-4e0a-9edc-00fedf7d4694/global")

        self.assertIsInstance(result, EventOrchestrationGlobal)
        self.assertIsNotNone(result.orchestration_path)
        self.assertEqual(result.orchestration_path.type, "global")
        self.assertEqual(result.orchestration_path.parent.id, "b02e973d-9620-4e0a-9edc-00fedf7d4694")
        self.assertEqual(result.orchestration_path.parent.type, "event_orchestration_reference")
        self.assertEqual(len(result.orchestration_path.sets), 1)
        self.assertEqual(result.orchestration_path.sets[0].id, "start")
        self.assertEqual(len(result.orchestration_path.sets[0].rules), 2)

        # Test drop_event action which is unique to global orchestrations
        drop_rule = result.orchestration_path.sets[0].rules[1]
        self.assertEqual(drop_rule.label, "Drop all events from the very-noisy monitoring tool")
        self.assertTrue(drop_rule.actions.drop_event)

    @patch("pagerduty_mcp.tools.event_orchestrations.get_client")
    def test_get_event_orchestration_global_direct_response(self, mock_get_client):
        """Test get_event_orchestration_global with direct response (no wrapper)."""
        sample_direct_response = {
            "type": "global",
            "parent": {
                "id": "GLOBAL123",
                "self": "https://api.pagerduty.com/event_orchestrations/GLOBAL123",
                "type": "event_orchestration_reference",
            },
            "self": "https://api.pagerduty.com/event_orchestrations/GLOBAL123/global",
            "sets": [
                {
                    "id": "start",
                    "rules": [
                        {
                            "label": "Test rule with drop_event",
                            "id": "drop_rule",
                            "conditions": [{"expression": "event.source matches 'spam'"}],
                            "actions": {"drop_event": True},
                        }
                    ],
                }
            ],
            "catch_all": {"actions": {"suppress": False}},
            "created_at": "2021-11-18T16:42:01Z",
            "updated_at": "2021-11-18T16:42:01Z",
            "version": "version456",
        }

        mock_client = MagicMock()
        mock_client.rget.return_value = sample_direct_response
        mock_get_client.return_value = mock_client

        result = get_event_orchestration_global("GLOBAL123")

        self.assertIsInstance(result, EventOrchestrationGlobal)
        self.assertEqual(result.orchestration_path.type, "global")
        self.assertEqual(result.orchestration_path.parent.id, "GLOBAL123")

    def test_event_orchestration_global_model_validation(self):
        """Test EventOrchestrationGlobal model validation."""
        test_data = {
            "orchestration_path": {
                "type": "global",
                "parent": {
                    "id": "GLOBAL123",
                    "self": "https://api.pagerduty.com/event_orchestrations/GLOBAL123",
                    "type": "event_orchestration_reference",
                },
                "sets": [
                    {
                        "id": "start",
                        "rules": [
                            {
                                "id": "rule1",
                                "label": "Drop noisy events",
                                "conditions": [{"expression": "event.source matches 'noisy'"}],
                                "actions": {"drop_event": True},
                            }
                        ],
                    }
                ],
                "catch_all": {"actions": {"suppress": True}},
            }
        }

        global_orch = EventOrchestrationGlobal.model_validate(test_data)

        self.assertEqual(global_orch.orchestration_path.type, "global")
        self.assertEqual(global_orch.orchestration_path.parent.id, "GLOBAL123")
        self.assertEqual(len(global_orch.orchestration_path.sets), 1)
        self.assertEqual(global_orch.orchestration_path.sets[0].rules[0].id, "rule1")
        self.assertTrue(global_orch.orchestration_path.sets[0].rules[0].actions.drop_event)

    def test_event_orchestration_global_from_api_response_wrapped(self):
        """Test EventOrchestrationGlobal.from_api_response with wrapped response."""
        wrapped_response = {
            "orchestration_path": {
                "type": "global",
                "parent": {
                    "id": "GLOBAL123",
                    "self": "https://api.pagerduty.com/event_orchestrations/GLOBAL123",
                    "type": "event_orchestration_reference",
                },
                "sets": [{"id": "start", "rules": []}],
                "catch_all": {"actions": {"suppress": True}},
            }
        }

        global_orch = EventOrchestrationGlobal.from_api_response(wrapped_response)

        self.assertIsInstance(global_orch, EventOrchestrationGlobal)
        self.assertEqual(global_orch.orchestration_path.type, "global")
        self.assertEqual(global_orch.orchestration_path.parent.id, "GLOBAL123")

    def test_event_orchestration_global_from_api_response_direct(self):
        """Test EventOrchestrationGlobal.from_api_response with direct response."""
        direct_response = {
            "type": "global",
            "parent": {
                "id": "GLOBAL123",
                "self": "https://api.pagerduty.com/event_orchestrations/GLOBAL123",
                "type": "event_orchestration_reference",
            },
            "sets": [{"id": "start", "rules": []}],
            "catch_all": {"actions": {"suppress": True}},
        }

        global_orch = EventOrchestrationGlobal.from_api_response(direct_response)

        self.assertIsInstance(global_orch, EventOrchestrationGlobal)
        self.assertEqual(global_orch.orchestration_path.type, "global")
        self.assertEqual(global_orch.orchestration_path.parent.id, "GLOBAL123")


if __name__ == "__main__":
    unittest.main()
