"""Tests for services-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class ServicesCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for services-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_services",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "SVC123", "name": "Web Service", "summary": "Main web application"},
                        {"id": "SVC456", "name": "Database Service", "summary": "Primary database"},
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_service",
                parameters=lambda params: params.get("service_id") == "SVC123",
                response={"id": "SVC123", "name": "Web Service", "summary": "Main web application"},
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_escalation_policies",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "EP123", "name": "Default EP", "summary": "Default escalation policy"},
                    ]
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
SERVICES_COMPETENCY_TESTS = [
    ServicesCompetencyTest(
        query="Show me all services",
        expected_tool_calls=[MockToolCall(name="list_services", parameters={})],
        description="Basic services listing",
    ),
    ServicesCompetencyTest(
        query="Get details for service SVC123",
        expected_tool_calls=[
            MockToolCall(name="get_service", parameters={"service_id": "SVC123"})
        ],
        description="Get specific service by ID",
    ),
    # Issue #4: create_service only requires escalation_policy.id, not summary
    ServicesCompetencyTest(
        query="Create a service named 'Payment API' with escalation policy EP123",
        expected_tool_calls=[
            MockToolCall(
                name="create_service",
                parameters={
                    "service_data": {
                        "service": {
                            "name": "Payment API",
                            "escalation_policy": {"id": "EP123"},
                        }
                    }
                },
            )
        ],
        description="Create service with escalation policy reference (only id required)",
    ),
    ServicesCompetencyTest(
        query=(
            "Create a service called 'Checkout Service' with description "
            "'Handles checkout flow' using escalation policy EP123"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_service",
                parameters={
                    "service_data": {
                        "service": {
                            "name": "Checkout Service",
                            "description": "Handles checkout flow",
                            "escalation_policy": {"id": "EP123"},
                        }
                    }
                },
            )
        ],
        description="Create service with description and escalation policy",
    ),
]
