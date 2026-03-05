"""Tests for schedules-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class SchedulesCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for schedules-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_schedules",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "SCHED123", "name": "Primary On-Call", "summary": "Primary on-call schedule"},
                        {"id": "SCHED456", "name": "Secondary On-Call", "summary": "Secondary on-call schedule"},
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_schedule",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response={"id": "SCHED123", "name": "Primary On-Call", "summary": "Primary on-call schedule"},
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_users",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "USER123", "name": "Alice", "email": "alice@example.com"},
                        {"id": "USER456", "name": "Bob", "email": "bob@example.com"},
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_schedule_users",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "USER123", "name": "Alice"},
                        {"id": "USER456", "name": "Bob"},
                    ]
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
SCHEDULES_COMPETENCY_TESTS = [
    SchedulesCompetencyTest(
        query="Show me all on-call schedules",
        expected_tool_calls=[MockToolCall(name="list_schedules", parameters={})],
        description="Basic schedules listing",
    ),
    SchedulesCompetencyTest(
        query="Get details for schedule SCHED123",
        expected_tool_calls=[
            MockToolCall(name="get_schedule", parameters={"schedule_id": "SCHED123"})
        ],
        description="Get specific schedule by ID",
    ),
    SchedulesCompetencyTest(
        query="Who is on schedule SCHED123?",
        expected_tool_calls=[
            MockToolCall(name="list_schedule_users", parameters={"schedule_id": "SCHED123"})
        ],
        description="List users on a schedule",
    ),
    # Issue #4: create_schedule_override uses 'overrides' key with array
    SchedulesCompetencyTest(
        query=(
            "Create a schedule override for schedule SCHED123 with user USER123 "
            "from 2024-01-15T09:00:00Z to 2024-01-15T17:00:00Z"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_schedule_override",
                parameters={
                    "schedule_id": "SCHED123",
                    "override_request": {
                        "overrides": [
                            {
                                "start": "2024-01-15T09:00:00Z",
                                "end": "2024-01-15T17:00:00Z",
                                "user_id": "USER123",
                            }
                        ]
                    },
                },
            )
        ],
        description="Create schedule override with overrides array format",
    ),
]
