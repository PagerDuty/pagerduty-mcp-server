"""Tests for priorities competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class PrioritiesCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for priorities queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_priorities",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "P1", "summary": "P1", "type": "priority_reference"},
                        {"id": "P2", "summary": "P2", "type": "priority_reference"},
                        {"id": "P3", "summary": "P3", "type": "priority_reference"},
                    ]
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
PRIORITIES_COMPETENCY_TESTS = [
    PrioritiesCompetencyTest(
        query="Show me all priorities",
        expected_tool_calls=[MockToolCall(name="list_priorities", parameters={})],
        description="List all configured priorities",
    ),
    PrioritiesCompetencyTest(
        query="List available priorities",
        expected_tool_calls=[MockToolCall(name="list_priorities", parameters={})],
        description="List priorities with natural language",
    ),
    PrioritiesCompetencyTest(
        query="What priorities are configured in PagerDuty?",
        expected_tool_calls=[MockToolCall(name="list_priorities", parameters={})],
        description="Query priorities as a question",
    ),
    PrioritiesCompetencyTest(
        query="Get the list of incident priorities",
        expected_tool_calls=[MockToolCall(name="list_priorities", parameters={})],
        description="Get incident priorities using natural language",
    ),
]
