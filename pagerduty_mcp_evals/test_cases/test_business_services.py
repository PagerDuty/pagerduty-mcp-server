"""Tests for business services competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class BusinessServicesCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for business services queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_business_services",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "BS1", "name": "Checkout Service"},
                        {"id": "BS2", "name": "Auth Service"},
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_business_service_dependencies",
                parameters=lambda params: True,
                response={
                    "relationships": [
                        {"id": "REL1", "type": "service_dependency"}
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_technical_service_dependencies",
                parameters=lambda params: True,
                response={
                    "relationships": [
                        {"id": "REL2", "type": "service_dependency"}
                    ]
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
BUSINESS_SERVICES_COMPETENCY_TESTS = [
    BusinessServicesCompetencyTest(
        query="List all business services",
        expected_tool_calls=[MockToolCall(name="list_business_services", parameters={})],
        description="Basic listing of all business services",
    ),
    BusinessServicesCompetencyTest(
        query="Show me the business services",
        expected_tool_calls=[MockToolCall(name="list_business_services", parameters={})],
        description="List business services with natural language",
    ),
    BusinessServicesCompetencyTest(
        query="Get dependencies for business service BS1",
        expected_tool_calls=[
            MockToolCall(
                name="get_business_service_dependencies",
                parameters={"business_service_id": "BS1"},
            )
        ],
        description="Get dependencies for a specific business service by ID",
    ),
    BusinessServicesCompetencyTest(
        query="What services depend on business service BS1?",
        expected_tool_calls=[
            MockToolCall(
                name="get_business_service_dependencies",
                parameters={"business_service_id": "BS1"},
            )
        ],
        description="Query business service dependencies as a question",
    ),
    BusinessServicesCompetencyTest(
        query="Show service dependencies for BS2",
        expected_tool_calls=[
            MockToolCall(
                name="get_business_service_dependencies",
                parameters={"business_service_id": "BS2"},
            )
        ],
        description="Get dependencies for a different business service",
    ),
    BusinessServicesCompetencyTest(
        query="Get dependencies for technical service SVC123",
        expected_tool_calls=[
            MockToolCall(
                name="get_technical_service_dependencies",
                parameters={"service_id": "SVC123"},
            )
        ],
        description="Get dependencies for a technical service by ID",
    ),
    BusinessServicesCompetencyTest(
        query="What does service SVC123 depend on?",
        expected_tool_calls=[
            MockToolCall(
                name="get_technical_service_dependencies",
                parameters={"service_id": "SVC123"},
            )
        ],
        description="Query technical service dependencies as a question",
    ),
]
