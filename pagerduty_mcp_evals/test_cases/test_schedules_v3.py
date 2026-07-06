"""Tests for v3 schedules competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)

_SAMPLE_SCHEDULE = {"id": "SCHED123", "name": "Engineering On-Call", "time_zone": "America/New_York"}
_SAMPLE_ROTATION = {"id": "ROT123", "type": "rotation"}
_SAMPLE_EVENT = {
    "id": "EVT123",
    "name": "Weekly On-Call",
    "recurrence": ["RRULE:FREQ=WEEKLY"],
    "effective_since": "2025-03-03T09:00:00Z",
}
_SAMPLE_CUSTOM_SHIFT = {
    "id": "CSHIFT123",
    "type": "custom_shift",
    "start_time": "2025-03-15T09:00:00Z",
    "end_time": "2025-03-15T17:00:00Z",
}
_SAMPLE_OVERRIDE = {
    "id": "OVRD123",
    "type": "override_shift",
    "start_time": "2025-03-15T09:00:00Z",
    "end_time": "2025-03-15T17:00:00Z",
}


class SchedulesV3CompetencyTest(AgentCompetencyTest):
    """AgentCompetencyTest specialization for v3 schedule queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_schedules_v3",
                parameters=lambda params: True,
                response={"response": [_SAMPLE_SCHEDULE]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_schedule_v3",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_SCHEDULE,
            ),
            MockMCPToolInvocationResponse(
                tool_name="create_schedule_v3",
                parameters=lambda params: True,
                response=_SAMPLE_SCHEDULE,
            ),
            MockMCPToolInvocationResponse(
                tool_name="update_schedule_v3",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_SCHEDULE,
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_schedule_v3_rotations",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response={"response": [_SAMPLE_ROTATION]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_schedule_v3_rotation",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_ROTATION,
            ),
            MockMCPToolInvocationResponse(
                tool_name="create_schedule_v3_rotation",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_ROTATION,
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_schedule_v3_rotation_events",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response={"response": [_SAMPLE_EVENT]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_schedule_v3_rotation_event",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_EVENT,
            ),
            MockMCPToolInvocationResponse(
                tool_name="create_schedule_v3_rotation_event",
                parameters=lambda params: True,
                response=_SAMPLE_EVENT,
            ),
            MockMCPToolInvocationResponse(
                tool_name="update_schedule_v3_rotation_event",
                parameters=lambda params: True,
                response=_SAMPLE_EVENT,
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_schedule_v3_custom_shifts",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response={"response": [_SAMPLE_CUSTOM_SHIFT]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_schedule_v3_custom_shift",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_CUSTOM_SHIFT,
            ),
            MockMCPToolInvocationResponse(
                tool_name="create_schedule_v3_custom_shifts",
                parameters=lambda params: True,
                response={"response": [_SAMPLE_CUSTOM_SHIFT]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_schedule_v3_overrides",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response={"response": [_SAMPLE_OVERRIDE]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_schedule_v3_override",
                parameters=lambda params: params.get("schedule_id") == "SCHED123",
                response=_SAMPLE_OVERRIDE,
            ),
            MockMCPToolInvocationResponse(
                tool_name="create_schedule_v3_overrides",
                parameters=lambda params: True,
                response={"response": [_SAMPLE_OVERRIDE]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="update_schedule_v3_override",
                parameters=lambda params: True,
                response=_SAMPLE_OVERRIDE,
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


SCHEDULES_V3_COMPETENCY_TESTS = [
    SchedulesV3CompetencyTest(
        query="List all v3 schedules in PagerDuty",
        expected_tool_calls=[MockToolCall(name="list_schedules_v3", parameters={})],
        description="List v3 schedules",
    ),
    SchedulesV3CompetencyTest(
        query="Get the v3 schedule with ID SCHED123",
        expected_tool_calls=[MockToolCall(name="get_schedule_v3", parameters={"schedule_id": "SCHED123"})],
        description="Get specific v3 schedule by ID",
    ),
    SchedulesV3CompetencyTest(
        query="Create a new v3 schedule called Engineering On-Call in the America/New_York timezone",
        expected_tool_calls=[
            MockToolCall(
                name="create_schedule_v3",
                parameters={
                    "schedule_data": {
                        "name": "Engineering On-Call",
                        "time_zone": "America/New_York",
                    }
                },
            )
        ],
        description="Create a v3 schedule",
    ),
    SchedulesV3CompetencyTest(
        query="List all rotations for v3 schedule SCHED123",
        expected_tool_calls=[
            MockToolCall(name="list_schedule_v3_rotations", parameters={"schedule_id": "SCHED123"})
        ],
        description="List rotations for a v3 schedule",
    ),
    SchedulesV3CompetencyTest(
        query="Create a new rotation in v3 schedule SCHED123",
        expected_tool_calls=[
            MockToolCall(name="create_schedule_v3_rotation", parameters={"schedule_id": "SCHED123"})
        ],
        description="Create a rotation in a v3 schedule",
    ),
    SchedulesV3CompetencyTest(
        query="List all events for rotation ROT123 in v3 schedule SCHED123",
        expected_tool_calls=[
            MockToolCall(
                name="list_schedule_v3_rotation_events",
                parameters={"schedule_id": "SCHED123", "rotation_id": "ROT123"},
            )
        ],
        description="List rotation events",
    ),
    SchedulesV3CompetencyTest(
        query=(
            "Create a weekly rotating on-call event in rotation ROT123 of schedule SCHED123 "
            "with users USER123 and USER456 starting 2025-03-03T09:00:00Z"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_schedule_v3_rotation_event",
                parameters={
                    "schedule_id": "SCHED123",
                    "rotation_id": "ROT123",
                },
            )
        ],
        description="Create a rotation event with rotating assignment",
    ),
    SchedulesV3CompetencyTest(
        query="List custom shifts for v3 schedule SCHED123 from 2025-03-01T00:00:00Z to 2025-03-31T23:59:59Z",
        expected_tool_calls=[
            MockToolCall(
                name="list_schedule_v3_custom_shifts",
                parameters={
                    "schedule_id": "SCHED123",
                    "since": "2025-03-01T00:00:00Z",
                    "until": "2025-03-31T23:59:59Z",
                },
            )
        ],
        description="List custom shifts with required time range",
    ),
    SchedulesV3CompetencyTest(
        query=(
            "Create a custom shift in schedule SCHED123 for user USER123 "
            "from 2025-03-15T09:00:00Z to 2025-03-15T17:00:00Z"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_schedule_v3_custom_shifts",
                parameters={"schedule_id": "SCHED123"},
            )
        ],
        description="Create a custom shift",
    ),
    SchedulesV3CompetencyTest(
        query="List overrides for v3 schedule SCHED123 from 2025-03-01T00:00:00Z to 2025-03-31T23:59:59Z",
        expected_tool_calls=[
            MockToolCall(
                name="list_schedule_v3_overrides",
                parameters={
                    "schedule_id": "SCHED123",
                    "since": "2025-03-01T00:00:00Z",
                    "until": "2025-03-31T23:59:59Z",
                },
            )
        ],
        description="List overrides with required time range",
    ),
    SchedulesV3CompetencyTest(
        query=(
            "Create an override in schedule SCHED123 for rotation ROT123 replacing user USER123 "
            "with user USER456 from 2025-03-15T09:00:00Z to 2025-03-15T17:00:00Z"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_schedule_v3_overrides",
                parameters={"schedule_id": "SCHED123"},
            )
        ],
        description="Create an override shift",
    ),
    SchedulesV3CompetencyTest(
        query=(
            "Update override OVRD123 in schedule SCHED123 so that user USER456 covers for user USER123 "
            "from 2025-03-15T09:00:00Z to 2025-03-15T19:00:00Z"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="update_schedule_v3_override",
                parameters={
                    "schedule_id": "SCHED123",
                    "override_id": "OVRD123",
                    "start_time": "2025-03-15T09:00:00Z",
                    "end_time": "2025-03-15T19:00:00Z",
                    "overridden_member_type": "user_member",
                    "overridden_member_user_id": "USER123",
                    "overriding_member_type": "user_member",
                    "overriding_member_user_id": "USER456",
                },
            )
        ],
        description="Update an override shift",
    ),
]
