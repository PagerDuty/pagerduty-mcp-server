"""Tests for Status Pages competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvokationResponse,
    MockToolCall,
)


class StatusPagesCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for Status Pages queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvokationResponse(
                tool_name="list_status_pages",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PT4KHLK",
                            "name": "My Brand Status Page",
                            "status_page_type": "public",
                            "url": "https://status.mybrand.example",
                        }
                    ]
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_status_page_severities",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PIJ90N7",
                            "description": "all good",
                            "post_type": "incident",
                        },
                        {
                            "id": "PF9KMXH",
                            "description": "minor",
                            "post_type": "incident",
                        },
                    ]
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_status_page_impacts",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PIJ90N7",
                            "description": "operational",
                            "post_type": "incident",
                        },
                        {
                            "id": "PF9KMXH",
                            "description": "partial outage",
                            "post_type": "incident",
                        },
                    ]
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_status_page_statuses",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PIJ90N7",
                            "description": "investigating",
                            "post_type": "incident",
                        },
                        {
                            "id": "PF9KMXH",
                            "description": "resolved",
                            "post_type": "incident",
                        },
                    ]
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="get_status_page_post",
                parameters=lambda params: True,
                response={
                    "id": "PIJ90N7",
                    "title": "Database Maintenance",
                    "post_type": "maintenance",
                    "status_page": {"id": "PT4KHLK", "type": "status_page"},
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_status_page_post_updates",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PXSOCH0",
                            "message": "Maintenance in progress",
                            "reviewed_status": "approved",
                        }
                    ]
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
STATUS_PAGES_COMPETENCY_TESTS = [
    StatusPagesCompetencyTest(
        query="List all status pages",
        expected_tool_calls=[
            MockToolCall(name="list_status_pages", parameters={"query_model": {}})
        ],
        description="Basic status pages listing",
    ),
    StatusPagesCompetencyTest(
        query="Show me only public status pages",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_pages",
                parameters={"query_model": {"status_page_type": "public"}},
            )
        ],
        description="List status pages filtered by type",
    ),
    StatusPagesCompetencyTest(
        query="List all severities for status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_severities",
                parameters={"status_page_id": "PT4KHLK", "query_model": {}},
            )
        ],
        description="List severities for a specific status page",
    ),
    StatusPagesCompetencyTest(
        query="Show me incident severities for status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_severities",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "query_model": {"post_type": "incident"},
                },
            )
        ],
        description="List severities filtered by post type",
    ),
    StatusPagesCompetencyTest(
        query="List all impacts for status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_impacts",
                parameters={"status_page_id": "PT4KHLK", "query_model": {}},
            )
        ],
        description="List impacts for a specific status page",
    ),
    StatusPagesCompetencyTest(
        query="Show me maintenance impacts for status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_impacts",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "query_model": {"post_type": "maintenance"},
                },
            )
        ],
        description="List impacts filtered by post type",
    ),
    StatusPagesCompetencyTest(
        query="List all statuses for status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_statuses",
                parameters={"status_page_id": "PT4KHLK", "query_model": {}},
            )
        ],
        description="List statuses for a specific status page",
    ),
    StatusPagesCompetencyTest(
        query="Show me incident statuses for status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_statuses",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "query_model": {"post_type": "incident"},
                },
            )
        ],
        description="List statuses filtered by post type",
    ),
    StatusPagesCompetencyTest(
        query="Get details for post PIJ90N7 on status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="get_status_page_post",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "query_model": {},
                },
            )
        ],
        description="Get a specific status page post",
    ),
    StatusPagesCompetencyTest(
        query="Get post PIJ90N7 on status page PT4KHLK with post updates included",
        expected_tool_calls=[
            MockToolCall(
                name="get_status_page_post",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "query_model": {"include": ["status_page_post_update"]},
                },
            )
        ],
        description="Get a status page post with included resources",
    ),
    StatusPagesCompetencyTest(
        query="List all post updates for post PIJ90N7 on status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_post_updates",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "query_model": {},
                },
            )
        ],
        description="List post updates for a specific post",
    ),
    StatusPagesCompetencyTest(
        query="Show me approved post updates for post PIJ90N7 on status page PT4KHLK",
        expected_tool_calls=[
            MockToolCall(
                name="list_status_page_post_updates",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "query_model": {"reviewed_status": "approved"},
                },
            )
        ],
        description="List post updates filtered by reviewed status",
    ),
    StatusPagesCompetencyTest(
        query=(
            "Create a maintenance post on status page PT4KHLK titled 'Database Upgrade' "
            "scheduled from 2023-12-12 11:00 to 12:00"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_status_page_post",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "create_model": {
                        "post": {
                            "title": "Database Upgrade",
                            "post_type": "maintenance",
                            "starts_at": "2023-12-12T11:00:00",
                            "ends_at": "2023-12-12T12:00:00",
                        }
                    },
                },
            )
        ],
        description="Create a maintenance status page post",
    ),
    StatusPagesCompetencyTest(
        query="Add an update to post PIJ90N7 on status page PT4KHLK with message 'Work in progress'",
        expected_tool_calls=[
            MockToolCall(
                name="create_status_page_post_update",
                parameters={
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "create_model": {"post_update": {"message": "Work in progress"}},
                },
            )
        ],
        description="Create a status page post update",
    ),
]
