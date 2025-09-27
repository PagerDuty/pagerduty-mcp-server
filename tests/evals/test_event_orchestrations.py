"""Tests for event-orchestrations-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class EventOrchestrationsCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for event-orchestrations-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        # Mock response for listing event orchestrations
        mcp.register_mock_response(
            "list_event_orchestrations",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "ORCH123",
                        "name": "Main Event Orchestration",
                        "description": "Primary orchestration for routing events",
                        "team": {"id": "TEAM123", "name": "Platform Team"},
                        "integrations": [{"id": "INTG123", "name": "Datadog Integration"}],
                    },
                    {
                        "id": "ORCH456",
                        "name": "Critical Services Orchestration",
                        "description": "Orchestration for critical service events",
                        "team": {"id": "TEAM456", "name": "SRE Team"},
                        "integrations": [{"id": "INTG456", "name": "Nagios Integration"}],
                    },
                ]
            },
        )

        # Mock response for getting a specific event orchestration
        mcp.register_mock_response(
            "get_event_orchestration",
            lambda params: params.get("orchestration_id") == "ORCH123",
            {
                "id": "ORCH123",
                "name": "Main Event Orchestration",
                "description": "Primary orchestration for routing events",
                "team": {"id": "TEAM123", "name": "Platform Team"},
                "integrations": [{"id": "INTG123", "name": "Datadog Integration"}],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
        )

        # Mock response for getting event orchestration router ORCH123
        mcp.register_mock_response(
            "get_event_orchestration_router",
            lambda params: params.get("orchestration_id") == "ORCH123",
            {
                "orchestration_path": {
                    "type": "router",
                    "sets": [
                        {
                            "id": "start",
                            "rules": [
                                {
                                    "id": "RULE001",
                                    "label": "Critical Events",
                                    "conditions": [{"expression": "event.severity matches 'critical'"}],
                                    "actions": {"route_to": "SVCORCH001"},
                                },
                                {
                                    "id": "RULE002",
                                    "label": "Warning Events",
                                    "conditions": [{"expression": "event.severity matches 'warning'"}],
                                    "actions": {"route_to": "SVCORCH002"},
                                },
                            ],
                        }
                    ],
                },
                "catch_all": {"actions": {"route_to": "unrouted"}},
            },
        )

        # Mock response for getting event orchestration router ORCH456
        mcp.register_mock_response(
            "get_event_orchestration_router",
            lambda params: params.get("orchestration_id") == "ORCH456",
            {
                "orchestration_path": {
                    "type": "router",
                    "sets": [
                        {
                            "id": "start",
                            "rules": [
                                {
                                    "id": "RULE003",
                                    "label": "High Severity Events",
                                    "conditions": [{"expression": "event.severity matches 'high'"}],
                                    "actions": {"route_to": "SVCORCH003"},
                                }
                            ],
                        }
                    ],
                },
                "catch_all": {"actions": {"route_to": "unrouted"}},
            },
        )

        # Mock response for updating event orchestration router
        mcp.register_mock_response(
            "update_event_orchestration_router",
            lambda params: params.get("orchestration_id") == "ORCH123",
            {
                "orchestration_path": {
                    "type": "router",
                    "sets": [
                        {
                            "id": "start",
                            "rules": [
                                {
                                    "id": "RULE001",
                                    "label": "Critical Events",
                                    "conditions": [{"expression": "event.severity matches 'critical'"}],
                                    "actions": {
                                        "route_to": "SVCORCH999"  # Updated to match the expected change
                                    },
                                }
                            ],
                        }
                    ],
                },
                "catch_all": {"actions": {"route_to": "unrouted"}},
            },
        )

        # Mock response for appending event orchestration router rule
        mcp.register_mock_response(
            "append_event_orchestration_router_rule",
            lambda params: params.get("orchestration_id") == "ORCH123",
            {
                "orchestration_path": {
                    "type": "router",
                    "sets": [
                        {
                            "id": "start",
                            "rules": [
                                {
                                    "id": "RULE001",
                                    "label": "Critical Events",
                                    "conditions": [{"expression": "event.severity matches 'critical'"}],
                                    "actions": {"route_to": "SVCORCH001"},
                                },
                                {
                                    "id": "RULE003",
                                    "label": "New Rule",
                                    "conditions": [{"expression": "event.component matches 'database'"}],
                                    "actions": {"route_to": "SVCORCH003"},
                                },
                            ],
                        }
                    ],
                },
                "catch_all": {"actions": {"route_to": "unrouted"}},
            },
        )


# Define the competency test cases
EVENT_ORCHESTRATIONS_COMPETENCY_TESTS = [
    # Basic listing tests
    EventOrchestrationsCompetencyTest(
        query="Show all event orchestrations in PagerDuty",
        expected_tools=[{"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}}],
        description="Basic event orchestrations listing",
    ),
    EventOrchestrationsCompetencyTest(
        query="List event orchestrations for the Platform Team",
        expected_tools=[
            {
                "tool_name": "list_event_orchestrations",
                "parameters": {"query_model": {}},
            }
        ],
        description="List event orchestrations filtered by team name (LLM filters client-side)",
    ),
    EventOrchestrationsCompetencyTest(
        query="Find all event orchestrations with 'critical' in the name",
        expected_tools=[
            {
                "tool_name": "list_event_orchestrations",
                "parameters": {"query_model": {}},
            }
        ],
        description="List event orchestrations filtered by name keyword (LLM filters client-side)",
    ),
    # Get specific event orchestration tests
    EventOrchestrationsCompetencyTest(
        query="Get details for event orchestration ORCH123",
        expected_tools=[{"tool_name": "get_event_orchestration", "parameters": {"orchestration_id": "ORCH123"}}],
        description="Get specific event orchestration by ID",
    ),
    EventOrchestrationsCompetencyTest(
        query="Tell me about the Main Event Orchestration",
        expected_tools=[
            {"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}},
            {"tool_name": "get_event_orchestration", "parameters": {"orchestration_id": "ORCH123"}},
        ],
        description="Get event orchestration by name (requires lookup)",
    ),
    # Router configuration tests
    EventOrchestrationsCompetencyTest(
        query="Show me the router configuration for event orchestration ORCH123",
        expected_tools=[{"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH123"}}],
        description="Get event orchestration router configuration",
    ),
    EventOrchestrationsCompetencyTest(
        query="What are the routing rules for the Main Event Orchestration?",
        expected_tools=[
            {"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}},
            {"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH123"}},
        ],
        description="Get router configuration by orchestration name (requires lookup)",
    ),
    # Router update tests
    EventOrchestrationsCompetencyTest(
        query=(
            "Update the router for event orchestration ORCH123 to route critical events to "
            "service orchestration SVCORCH999"
        ),
        expected_tools=[
            {"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH123"}},
            {
                "tool_name": "update_event_orchestration_router",
                "parameters": {
                    "orchestration_id": "ORCH123",
                    "router_update": {
                        "orchestration_path": {
                            "type": "router",
                            "sets": [
                                {
                                    "id": "start",
                                    "rules": [
                                        {
                                            "id": "RULE001",
                                            "label": "Critical Events",
                                            "conditions": [{"expression": "event.severity matches 'critical'"}],
                                            "actions": {"route_to": "SVCORCH999"},
                                        },
                                        {
                                            "id": "RULE002",
                                            "label": "Warning Events",
                                            "conditions": [{"expression": "event.severity matches 'warning'"}],
                                            "actions": {"route_to": "SVCORCH002"},
                                        },
                                    ],
                                }
                            ],
                            "catch_all": {"actions": {"route_to": "unrouted"}},
                        }
                    },
                },
            },
        ],
        description="Update event orchestration router configuration",
    ),
    # Append router rule tests
    EventOrchestrationsCompetencyTest(
        query=(
            "Add a new routing rule to event orchestration ORCH123 that routes database events to "
            "service orchestration SVCORCH003"
        ),
        expected_tools=[
            {
                "tool_name": "append_event_orchestration_router_rule",
                "parameters": {
                    "orchestration_id": "ORCH123",
                },
            }
        ],
        description="Append new routing rule to event orchestration",
    ),
    EventOrchestrationsCompetencyTest(
        query=(
            "Create a routing rule for the Main Event Orchestration to handle high priority alerts "
            "and route them to SVCORCH999"
        ),
        expected_tools=[
            {"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}},
            {
                "tool_name": "append_event_orchestration_router_rule",
                "parameters": {
                    "orchestration_id": "ORCH123",
                },
            },
        ],
        description="Append routing rule by orchestration name (requires lookup)",
    ),
    # Complex workflow tests
    EventOrchestrationsCompetencyTest(
        query="Show me all event orchestrations and then get the router configuration for the first one",
        expected_tools=[
            {"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}},
            {"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH123"}},
        ],
        description="Multi-step workflow: list orchestrations then get router config",
    ),
    EventOrchestrationsCompetencyTest(
        query="Find the Critical Services Orchestration and show me its routing rules",
        expected_tools=[
            {"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}},
            {"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH456"}},
        ],
        description="Complex workflow: find orchestration by name and get its router config",
    ),
    # Error handling scenarios
    EventOrchestrationsCompetencyTest(
        query="Get event orchestration with ID NONEXISTENT123",
        expected_tools=[{"tool_name": "get_event_orchestration", "parameters": {"orchestration_id": "NONEXISTENT123"}}],
        description="Handle non-existent event orchestration ID",
    ),
    # Edge cases
    EventOrchestrationsCompetencyTest(
        query="How many event orchestrations do we have?",
        expected_tools=[{"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}}],
        description="Count event orchestrations (requires listing all)",
    ),
    EventOrchestrationsCompetencyTest(
        query="Which event orchestration has the most routing rules?",
        expected_tools=[
            {"tool_name": "list_event_orchestrations", "parameters": {"query_model": {}}},
            {"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH123"}},
            {"tool_name": "get_event_orchestration_router", "parameters": {"orchestration_id": "ORCH456"}},
        ],
        description="Complex analysis requiring multiple router config lookups",
    ),
]
