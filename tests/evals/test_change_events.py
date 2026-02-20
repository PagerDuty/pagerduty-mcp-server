"""Tests for change events competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class ChangeEventsCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for change events queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_change_events",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "CHE123ABC",
                        "summary": "Deployed version 2.1.0 to production",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "type": "change_event",
                        "services": [{"id": "SERV123", "type": "service_reference", "summary": "Web Service"}],
                    }
                ]
            },
        )
        mcp.register_mock_response(
            "get_change_event",
            lambda params: True,
            {
                "id": "CHE123ABC",
                "summary": "Deployed version 2.1.0 to production",
                "timestamp": "2024-01-15T10:30:00Z",
                "type": "change_event",
                "services": [{"id": "SERV123", "type": "service_reference", "summary": "Web Service"}],
                "integration": {"id": "INT456", "type": "integration_reference", "summary": "GitHub Integration"},
                "source": "github.com/example/repo",
                "custom_details": {"version": "2.1.0", "environment": "production"},
            },
        )
        mcp.register_mock_response(
            "list_service_change_events",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "CHE456DEF",
                        "summary": "Database schema migration",
                        "timestamp": "2024-01-14T15:20:00Z",
                        "type": "change_event",
                        "services": [{"id": "SERV123", "type": "service_reference", "summary": "Web Service"}],
                    }
                ]
            },
        )
        mcp.register_mock_response(
            "list_incident_change_events",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "CHE789GHI",
                        "summary": "Configuration update",
                        "timestamp": "2024-01-13T08:45:00Z",
                        "type": "change_event",
                        "services": [{"id": "SERV123", "type": "service_reference", "summary": "Web Service"}],
                    }
                ]
            },
        )


# Define the competency test cases
CHANGE_EVENTS_COMPETENCY_TESTS = [
    ChangeEventsCompetencyTest(
        query="List all change events",
        expected_tools=[{"tool_name": "list_change_events", "parameters": {"query_model": None}}],
        description="Basic change events listing",
    ),
    ChangeEventsCompetencyTest(
        query="Show me recent change events",
        expected_tools=[{"tool_name": "list_change_events", "parameters": {"query_model": None}}],
        description="Basic change events listing with natural language",
    ),
    ChangeEventsCompetencyTest(
        query="Show me the first 10 change events",
        expected_tools=[{"tool_name": "list_change_events", "parameters": {"query_model": {"limit": 10}}}],
        description="List change events with limit parameter",
    ),
    ChangeEventsCompetencyTest(
        query="List change events for team TEAM123",
        expected_tools=[
            {"tool_name": "list_change_events", "parameters": {"query_model": {"team_ids": ["TEAM123"]}}}
        ],
        description="List change events filtered by team",
    ),
    ChangeEventsCompetencyTest(
        query="Show change events for integration INT456",
        expected_tools=[
            {"tool_name": "list_change_events", "parameters": {"query_model": {"integration_ids": ["INT456"]}}}
        ],
        description="List change events filtered by integration",
    ),
    ChangeEventsCompetencyTest(
        query="Get change event CHE123ABC",
        expected_tools=[{"tool_name": "get_change_event", "parameters": {"change_event_id": "CHE123ABC"}}],
        description="Get specific change event by ID",
    ),
    ChangeEventsCompetencyTest(
        query="Show me details for change event ID XYZ789",
        expected_tools=[{"tool_name": "get_change_event", "parameters": {"change_event_id": "XYZ789"}}],
        description="Get specific change event by ID with natural language",
    ),
    ChangeEventsCompetencyTest(
        query="Tell me about change event CHE123ABC",
        expected_tools=[{"tool_name": "get_change_event", "parameters": {"change_event_id": "CHE123ABC"}}],
        description="Get change event details with different wording",
    ),
    ChangeEventsCompetencyTest(
        query="List change events for service P43PBXB",
        expected_tools=[
            {
                "tool_name": "list_service_change_events",
                "parameters": {"service_id": "P43PBXB", "query_model": None},
            }
        ],
        description="List change events for a specific service",
    ),
    ChangeEventsCompetencyTest(
        query="Show me recent changes for service P43PBXB",
        expected_tools=[
            {"tool_name": "list_service_change_events", "parameters": {"service_id": "P43PBXB", "query_model": None}}
        ],
        description="List service change events with natural language",
    ),
    ChangeEventsCompetencyTest(
        query="Get the first 5 change events for service P43PBXB",
        expected_tools=[
            {
                "tool_name": "list_service_change_events",
                "parameters": {"service_id": "P43PBXB", "query_model": {"limit": 5}},
            }
        ],
        description="List service change events with limit",
    ),
    ChangeEventsCompetencyTest(
        query="List change events related to incident Q3QCNPM78BXOAL",
        expected_tools=[
            {"tool_name": "list_incident_change_events", "parameters": {"incident_id": "Q3QCNPM78BXOAL"}}
        ],
        description="List change events related to an incident",
    ),
    ChangeEventsCompetencyTest(
        query="Show me what changed before incident Q3QCNPM78BXOAL",
        expected_tools=[
            {"tool_name": "list_incident_change_events", "parameters": {"incident_id": "Q3QCNPM78BXOAL"}}
        ],
        description="List incident-related change events with natural language",
    ),
    ChangeEventsCompetencyTest(
        query="Get change events for incident Q3QCNPM78BXOAL with limit 5",
        expected_tools=[
            {"tool_name": "list_incident_change_events", "parameters": {"incident_id": "Q3QCNPM78BXOAL", "limit": 5}}
        ],
        description="List incident change events with limit parameter",
    ),
    ChangeEventsCompetencyTest(
        query="Show me changes that may have caused incident Q3QCNPM78BXOAL",
        expected_tools=[
            {"tool_name": "list_incident_change_events", "parameters": {"incident_id": "Q3QCNPM78BXOAL"}}
        ],
        description="List incident-related change events with causal language",
    ),
]
