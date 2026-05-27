"""Tests for on-call compensation competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)

_MOCK_COMPENSATION_REPORT = {
    "since": "2023-01-01T00:00:00Z",
    "until": "2023-01-31T23:59:59Z",
    "timezone": "UTC",
    "compliance_template": "none",
    "generated_at": "2023-02-01T10:00:00Z",
    "total_users": 2,
    "total_scheduled_hours": 240.0,
    "total_outside_hours": 80.0,
    "total_estimated_pay": 0.0,
    "compliance_violations": 0,
    "compliance_near_limit": 0,
    "is_forward": False,
    "users": [
        {
            "user_id": "U1",
            "user_name": "Alice",
            "scheduled_hours": 160.0,
            "outside_hours": 48.0,
            "total_interruptions": 10,
        }
    ],
    "team_summary": [{"team_name": "Engineering", "user_count": 2}],
}


class OncallCompensationCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for on-call compensation queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="get_oncall_compensation_report",
                parameters=lambda params: True,
                response=_MOCK_COMPENSATION_REPORT,
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
ONCALL_COMPENSATION_COMPETENCY_TESTS = [
    OncallCompensationCompetencyTest(
        query="Generate an on-call compensation report for January 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2023-01-01T00:00:00Z",
                    "until": "2023-01-31T23:59:59Z",
                },
            )
        ],
        description="Generate a basic on-call compensation report for a month",
    ),
    OncallCompensationCompetencyTest(
        query="Show me who was on call the most from 2023-01-01 to 2023-01-31",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2023-01-01T00:00:00Z",
                    "until": "2023-01-31T23:59:59Z",
                },
            )
        ],
        description="Find the most on-call user for a date range",
    ),
    OncallCompensationCompetencyTest(
        query="Generate an on-call compensation report from 2023-01-01 to 2023-03-31 for team_ids T1",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2023-01-01T00:00:00Z",
                    "until": "2023-03-31T23:59:59Z",
                    "team_ids": ["T1"],
                },
            )
        ],
        description="Get on-call compensation report filtered by team",
    ),
    OncallCompensationCompetencyTest(
        query="Generate a pay estimation report for January 2023 at $10/hour",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2023-01-01T00:00:00Z",
                    "until": "2023-01-31T23:59:59Z",
                    "l1_rate_per_hour": 10.0,
                },
            )
        ],
        description="Generate pay estimation with hourly rate",
    ),
    OncallCompensationCompetencyTest(
        query="Check EU compliance for January 2023 on-call shifts",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2023-01-01T00:00:00Z",
                    "until": "2023-01-31T23:59:59Z",
                    "compliance_template": "emea",
                },
            )
        ],
        description="Generate on-call report with EMEA compliance template",
    ),
    OncallCompensationCompetencyTest(
        query="Project on-call costs for May 2026 (2026-05-01 to 2026-05-31)",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2026-05-01T00:00:00Z",
                    "until": "2026-05-31T23:59:59Z",
                    "forward": True,
                },
            )
        ],
        description="Project on-call costs for a future month using forward mode",
    ),
    OncallCompensationCompetencyTest(
        query="Use get_oncall_compensation_report in forward mode to project on-call burden from 2026-06-01 to 2026-06-30",
        expected_tool_calls=[
            MockToolCall(
                name="get_oncall_compensation_report",
                parameters={
                    "since": "2026-06-01T00:00:00Z",
                    "until": "2026-06-30T23:59:59Z",
                    "forward": True,
                },
            )
        ],
        description="Query scheduled on-call shifts for a future date range using forward mode",
    ),
]
