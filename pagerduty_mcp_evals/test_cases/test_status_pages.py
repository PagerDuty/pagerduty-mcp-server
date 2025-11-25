"""Tests for Status Pages competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class StatusPagesCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for Status Pages queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_status_pages",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "PT4KHLK",
                        "name": "My Brand Status Page",
                        "status_page_type": "public",
                        "url": "https://status.mybrand.example",
                    }
                ]
            },
        )
        mcp.register_mock_response(
            "list_status_page_severities",
            lambda params: True,
            {
                "response": [
                    {"id": "PIJ90N7", "description": "all good", "post_type": "incident"},
                    {"id": "PF9KMXH", "description": "minor", "post_type": "incident"},
                ]
            },
        )
        mcp.register_mock_response(
            "list_status_page_impacts",
            lambda params: True,
            {
                "response": [
                    {"id": "PIJ90N7", "description": "operational", "post_type": "incident"},
                    {"id": "PF9KMXH", "description": "partial outage", "post_type": "incident"},
                ]
            },
        )
        mcp.register_mock_response(
            "list_status_page_statuses",
            lambda params: True,
            {
                "response": [
                    {"id": "PIJ90N7", "description": "investigating", "post_type": "incident"},
                    {"id": "PF9KMXH", "description": "resolved", "post_type": "incident"},
                ]
            },
        )
        mcp.register_mock_response(
            "get_status_page_post",
            lambda params: True,
            {
                "id": "PIJ90N7",
                "title": "Database Maintenance",
                "post_type": "maintenance",
                "status_page": {"id": "PT4KHLK", "type": "status_page"},
            },
        )
        mcp.register_mock_response(
            "list_status_page_post_updates",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "PXSOCH0",
                        "message": "Maintenance in progress",
                        "reviewed_status": "approved",
                    }
                ]
            },
        )


# Define the competency test cases
STATUS_PAGES_COMPETENCY_TESTS = [
    StatusPagesCompetencyTest(
        query="List all status pages",
        expected_tools=[{"tool_name": "list_status_pages", "parameters": {"query_model": {}}}],
        description="Basic status pages listing",
    ),
    StatusPagesCompetencyTest(
        query="Show me only public status pages",
        expected_tools=[
            {
                "tool_name": "list_status_pages",
                "parameters": {"query_model": {"status_page_type": "public"}},
            }
        ],
        description="List status pages filtered by type",
    ),
    StatusPagesCompetencyTest(
        query="List all severities for status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_severities",
                "parameters": {"status_page_id": "PT4KHLK", "query_model": {}},
            }
        ],
        description="List severities for a specific status page",
    ),
    StatusPagesCompetencyTest(
        query="Show me incident severities for status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_severities",
                "parameters": {"status_page_id": "PT4KHLK", "query_model": {"post_type": "incident"}},
            }
        ],
        description="List severities filtered by post type",
    ),
    StatusPagesCompetencyTest(
        query="List all impacts for status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_impacts",
                "parameters": {"status_page_id": "PT4KHLK", "query_model": {}},
            }
        ],
        description="List impacts for a specific status page",
    ),
    StatusPagesCompetencyTest(
        query="Show me maintenance impacts for status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_impacts",
                "parameters": {"status_page_id": "PT4KHLK", "query_model": {"post_type": "maintenance"}},
            }
        ],
        description="List impacts filtered by post type",
    ),
    StatusPagesCompetencyTest(
        query="List all statuses for status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_statuses",
                "parameters": {"status_page_id": "PT4KHLK", "query_model": {}},
            }
        ],
        description="List statuses for a specific status page",
    ),
    StatusPagesCompetencyTest(
        query="Show me incident statuses for status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_statuses",
                "parameters": {"status_page_id": "PT4KHLK", "query_model": {"post_type": "incident"}},
            }
        ],
        description="List statuses filtered by post type",
    ),
    StatusPagesCompetencyTest(
        query="Get details for post PIJ90N7 on status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "get_status_page_post",
                "parameters": {"status_page_id": "PT4KHLK", "post_id": "PIJ90N7", "query_model": {}},
            }
        ],
        description="Get a specific status page post",
    ),
    StatusPagesCompetencyTest(
        query="Get post PIJ90N7 on status page PT4KHLK with post updates included",
        expected_tools=[
            {
                "tool_name": "get_status_page_post",
                "parameters": {
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "query_model": {"include": ["status_page_post_update"]},
                },
            }
        ],
        description="Get a status page post with included resources",
    ),
    StatusPagesCompetencyTest(
        query="List all post updates for post PIJ90N7 on status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_post_updates",
                "parameters": {"status_page_id": "PT4KHLK", "post_id": "PIJ90N7", "query_model": {}},
            }
        ],
        description="List post updates for a specific post",
    ),
    StatusPagesCompetencyTest(
        query="Show me approved post updates for post PIJ90N7 on status page PT4KHLK",
        expected_tools=[
            {
                "tool_name": "list_status_page_post_updates",
                "parameters": {
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "query_model": {"reviewed_status": "approved"},
                },
            }
        ],
        description="List post updates filtered by reviewed status",
    ),
    StatusPagesCompetencyTest(
        query=(
            "Create a maintenance post on status page PT4KHLK titled 'Database Upgrade' "
            "scheduled from 2023-12-12 11:00 to 12:00"
        ),
        expected_tools=[
            {
                "tool_name": "create_status_page_post",
                "parameters": {
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
            }
        ],
        description="Create a maintenance status page post",
    ),
    StatusPagesCompetencyTest(
        query="Add an update to post PIJ90N7 on status page PT4KHLK with message 'Work in progress'",
        expected_tools=[
            {
                "tool_name": "create_status_page_post_update",
                "parameters": {
                    "status_page_id": "PT4KHLK",
                    "post_id": "PIJ90N7",
                    "create_model": {"post_update": {"message": "Work in progress"}},
                },
            }
        ],
        description="Create a status page post update",
    ),
]
