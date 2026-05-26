"""Tests for analytics competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class AnalyticsCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for analytics queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="get_responder_metrics",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "responder_id": "U1",
                            "responder_name": "Alice",
                            "team_id": "T1",
                            "team_name": "Engineering",
                            "total_seconds_on_call": 72000,
                            "total_incident_count": 5,
                            "total_interruptions": 8,
                            "total_business_hour_interruptions": 3,
                            "total_off_hour_interruptions": 3,
                            "total_sleep_hour_interruptions": 2,
                        }
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_incident_metrics_by_service",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "service_id": "SVC1",
                            "service_name": "Web Service",
                            "total_incident_count": 5,
                            "mean_seconds_to_first_ack": 120,
                            "mean_seconds_to_resolve": 3600,
                        }
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_incident_metrics_by_team",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "team_id": "T1",
                            "team_name": "Engineering",
                            "total_incident_count": 12,
                            "mean_seconds_to_first_ack": 180,
                            "mean_seconds_to_resolve": 7200,
                        }
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_responder_load_metrics",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "responder_id": "U1",
                            "responder_name": "Alice",
                            "total_seconds_on_call": 72000,
                            "total_incident_count": 5,
                            "total_interruptions": 8,
                            "total_sleep_hour_interruptions": 2,
                        }
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_incident_metrics_all",
                parameters=lambda params: True,
                response={
                    "total_incident_count": 42,
                    "mean_seconds_to_first_ack": 150,
                    "mean_seconds_to_resolve": 5400,
                    "p50_seconds_to_resolve": 3600,
                    "p90_seconds_to_resolve": 10800,
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
ANALYTICS_COMPETENCY_TESTS = [
    AnalyticsCompetencyTest(
        query="Show me responder metrics for January 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_responder_metrics",
                parameters={
                    "request": {
                        "filters": {
                            "date_range_start": "2023-01-01T00:00:00Z",
                            "date_range_end": "2023-01-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get responder metrics for a specific month",
    ),
    AnalyticsCompetencyTest(
        query="Get on-call burden data for the engineering team T1 in Q1 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_responder_metrics",
                parameters={
                    "request": {
                        "filters": {
                            "date_range_start": "2023-01-01T00:00:00Z",
                            "date_range_end": "2023-03-31T23:59:59Z",
                            "team_ids": ["T1"],
                        }
                    }
                },
            )
        ],
        description="Get responder metrics filtered by team ID",
    ),
    AnalyticsCompetencyTest(
        query="Show incident metrics by service for January 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_metrics_by_service",
                parameters={
                    "request": {
                        "filters": {
                            "created_at_start": "2023-01-01T00:00:00Z",
                            "created_at_end": "2023-01-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get incident metrics grouped by service",
    ),
    AnalyticsCompetencyTest(
        query="Get incident count by service for January 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_metrics_by_service",
                parameters={
                    "request": {
                        "filters": {
                            "created_at_start": "2023-01-01T00:00:00Z",
                            "created_at_end": "2023-01-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get incident counts per service with date range",
    ),
    AnalyticsCompetencyTest(
        query="Show team incident metrics for Q1 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_metrics_by_team",
                parameters={
                    "request": {
                        "filters": {
                            "created_at_start": "2023-01-01T00:00:00Z",
                            "created_at_end": "2023-03-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get incident metrics grouped by team",
    ),
    AnalyticsCompetencyTest(
        query="Get responder load metrics for January 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_responder_load_metrics",
                parameters={
                    "request": {
                        "filters": {
                            "date_range_start": "2023-01-01T00:00:00Z",
                            "date_range_end": "2023-01-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get responder load metrics for a date range",
    ),
    AnalyticsCompetencyTest(
        query="Show all incident metrics for January 2023 aggregated by week",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_metrics_all",
                parameters={
                    "request": {
                        "filters": {
                            "created_at_start": "2023-01-01T00:00:00Z",
                            "created_at_end": "2023-01-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get all incident metrics with aggregate_unit=week",
    ),
    AnalyticsCompetencyTest(
        query="Get a breakdown of incidents for all teams in January 2023",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_metrics_all",
                parameters={
                    "request": {
                        "filters": {
                            "created_at_start": "2023-01-01T00:00:00Z",
                            "created_at_end": "2023-01-31T23:59:59Z",
                        }
                    }
                },
            )
        ],
        description="Get rollup incident metrics for all teams",
    ),
]
