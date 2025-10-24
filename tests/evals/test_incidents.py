"""Tests for incident-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class IncidentCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for incident-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_teams", lambda params: True, {"response": [{"id": "TEAM123", "name": "Dev Team"}]}
        )
        mcp.register_mock_response(
            "list_services", lambda params: True, {"response": [{"id": "SVC123", "name": "Web Service"}]}
        )
        mcp.register_mock_response(
            "get_outlier_incident",
            lambda params: True,
            {"response": {"outliers": [{"id": "OUT123", "similarity_score": 0.85}]}},
        )
        mcp.register_mock_response(
            "get_past_incidents",
            lambda params: True,
            {"response": {"incidents": [{"id": "PAST123", "similarity_score": 0.92}]}},
        )
        mcp.register_mock_response(
            "get_related_incidents",
            lambda params: True,
            {"response": {"incidents": [{"id": "REL123", "title": "Related incident"}]}},
        )


# Define the competency test cases
INCIDENT_COMPETENCY_TESTS = [
    IncidentCompetencyTest(
        query="Show me all open and resolved incidents",
        expected_tools=[
            {
                "tool_name": "list_incidents",
                "parameters": {"query_model": {"status": ["triggered", "acknowledged", "resolved"]}},
            }
        ],
        description="List incidents filtered by status",
    ),
    IncidentCompetencyTest(
        query="List open incidents",
        expected_tools=[
            {"tool_name": "list_incidents", "parameters": {"query_model": {"status": ["triggered", "acknowledged"]}}}
        ],
        description="List incidents filtered by status",
    ),
    IncidentCompetencyTest(
        query="Show me all incidents",
        expected_tools=[{"tool_name": "list_incidents", "parameters": {}}],
        description="Basic incident listing",
    ),
    IncidentCompetencyTest(
        query="Show me all triggered incidents",
        expected_tools=[{"tool_name": "list_incidents", "parameters": {"query_model": {"status": ["triggered"]}}}],
        description="List incidents filtered by status",
    ),
    IncidentCompetencyTest(
        query="Tell me about incident 123",
        expected_tools=[{"tool_name": "get_incident", "parameters": {"incident_id": "123"}}],
        description="Get specific incident by number",
    ),
    IncidentCompetencyTest(
        query="Create an incident with title 'Testing MCP' for service with ID 1234 with high urgency",
        expected_tools=[
            {
                "tool_name": "create_incident",
                "parameters": {
                    "create_model": {
                        "incident": {
                            "title": "Testing MCP",
                            "service": {"id": "1234"},
                        }
                    }
                },
            }
        ],
        description="Create incident for team (allows team lookup)",
    ),
    IncidentCompetencyTest(
        query="Create a high urgency incident titled 'Server down' for the Website service",
        expected_tools=[
            {
                "tool_name": "create_incident",
                "parameters": {"create_model": {"incident": {"title": "Server down", "urgency": "high"}}},
            }
        ],
        description="Create incident for service (allows service lookup)",
    ),
    IncidentCompetencyTest(
        query="Acknowledge incident 456",
        expected_tools=[
            {
                "tool_name": "manage_incidents",
                "parameters": {"manage_request": {"incident_ids": ["456"], "status": "acknowledged"}},
            }
        ],
        description="Acknowledge specific incident",
    ),
    IncidentCompetencyTest(
        query="Show me outlier analysis for incident 789",
        expected_tools=[
            {
                "tool_name": "get_outlier_incident",
                "parameters": {"query_model": {"incident_id": "789"}},
            }
        ],
        description="Get outlier incident information using specialized tool",
    ),
    IncidentCompetencyTest(
        query="Show me similar past incidents for incident ABC123",
        expected_tools=[
            {
                "tool_name": "get_past_incidents",
                "parameters": {"query_model": {"incident_id": "ABC123"}},
            }
        ],
        description="Get past incidents using specialized tool",
    ),
    IncidentCompetencyTest(
        query="Show me related incidents for incident DEF456",
        expected_tools=[
            {
                "tool_name": "get_related_incidents",
                "parameters": {"query_model": {"incident_id": "DEF456"}},
            }
        ],
        description="Get related incidents using specialized tool",
    ),
]
