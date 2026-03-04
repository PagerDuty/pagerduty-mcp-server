"""Tests for schedules-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class SchedulesCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for schedules-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_schedules",
            lambda params: True,
            {
                "response": [
                    {"id": "SCHED123", "name": "Primary On-Call", "summary": "Primary on-call schedule"},
                    {"id": "SCHED456", "name": "Secondary On-Call", "summary": "Secondary on-call schedule"},
                ]
            },
        )
        mcp.register_mock_response(
            "get_schedule",
            lambda params: params.get("schedule_id") == "SCHED123",
            {"id": "SCHED123", "name": "Primary On-Call", "summary": "Primary on-call schedule"},
        )
        mcp.register_mock_response(
            "list_users",
            lambda params: True,
            {
                "response": [
                    {"id": "USER123", "name": "Alice", "email": "alice@example.com"},
                    {"id": "USER456", "name": "Bob", "email": "bob@example.com"},
                ]
            },
        )
        mcp.register_mock_response(
            "list_schedule_users",
            lambda params: True,
            {
                "response": [
                    {"id": "USER123", "name": "Alice"},
                    {"id": "USER456", "name": "Bob"},
                ]
            },
        )


# Define the competency test cases
SCHEDULES_COMPETENCY_TESTS = [
    SchedulesCompetencyTest(
        query="Show me all on-call schedules",
        expected_tools=[{"tool_name": "list_schedules", "parameters": {}}],
        description="Basic schedules listing",
    ),
    SchedulesCompetencyTest(
        query="Get details for schedule SCHED123",
        expected_tools=[{"tool_name": "get_schedule", "parameters": {"schedule_id": "SCHED123"}}],
        description="Get specific schedule by ID",
    ),
    SchedulesCompetencyTest(
        query="Who is on schedule SCHED123?",
        expected_tools=[{"tool_name": "list_schedule_users", "parameters": {"schedule_id": "SCHED123"}}],
        description="List users on a schedule",
    ),
    # Issue #4: create_schedule_override uses 'overrides' key with array
    SchedulesCompetencyTest(
        query=(
            "Create a schedule override for schedule SCHED123 with user USER123 "
            "from 2024-01-15T09:00:00Z to 2024-01-15T17:00:00Z"
        ),
        expected_tools=[
            {
                "tool_name": "create_schedule_override",
                "parameters": {
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
            }
        ],
        description="Create schedule override with overrides array format",
    ),
]
