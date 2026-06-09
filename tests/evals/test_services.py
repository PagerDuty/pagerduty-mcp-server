"""Tests for services-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class ServicesCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for services-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_services",
            lambda params: True,
            {
                "response": [
                    {"id": "SVC123", "name": "Web Service", "summary": "Main web application"},
                    {"id": "SVC456", "name": "Database Service", "summary": "Primary database"},
                ]
            },
        )
        mcp.register_mock_response(
            "get_service",
            lambda params: params.get("service_id") == "SVC123",
            {"id": "SVC123", "name": "Web Service", "summary": "Main web application"},
        )
        mcp.register_mock_response(
            "list_escalation_policies",
            lambda params: True,
            {
                "response": [
                    {"id": "EP123", "name": "Default EP", "summary": "Default escalation policy"},
                ]
            },
        )


# Define the competency test cases
SERVICES_COMPETENCY_TESTS = [
    ServicesCompetencyTest(
        query="Show me all services",
        expected_tools=[{"tool_name": "list_services", "parameters": {}}],
        description="Basic services listing",
    ),
    ServicesCompetencyTest(
        query="Get details for service SVC123",
        expected_tools=[{"tool_name": "get_service", "parameters": {"service_id": "SVC123"}}],
        description="Get specific service by ID",
    ),
    # Issue #4: create_service only requires escalation_policy.id, not summary
    ServicesCompetencyTest(
        query="Create a service named 'Payment API' with escalation policy EP123",
        expected_tools=[
            {
                "tool_name": "create_service",
                "parameters": {
                    "service_data": {
                        "service": {
                            "name": "Payment API",
                            "escalation_policy": {"id": "EP123"},
                        }
                    }
                },
            }
        ],
        description="Create service with escalation policy reference (only id required)",
    ),
    ServicesCompetencyTest(
        query=(
            "Create a service called 'Checkout Service' with description "
            "'Handles checkout flow' using escalation policy EP123"
        ),
        expected_tools=[
            {
                "tool_name": "create_service",
                "parameters": {
                    "service_data": {
                        "service": {
                            "name": "Checkout Service",
                            "description": "Handles checkout flow",
                            "escalation_policy": {"id": "EP123"},
                        }
                    }
                },
            }
        ],
        description="Create service with description and escalation policy",
    ),
]
