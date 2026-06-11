"""Tests for log entry-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class LogEntryCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for log entry-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_log_entries",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PLOGENTRY123",
                            "type": "trigger_log_entry",
                            "summary": "Triggered via the website",
                            "self": "https://api.pagerduty.com/log_entries/PLOGENTRY123",
                            "html_url": "https://subdomain.pagerduty.com/incidents/PINCIDENT123/log_entries/PLOGENTRY123",
                            "created_at": "2015-10-06T21:30:42Z",
                            "agent": {
                                "id": "PUSER123",
                                "type": "user_reference",
                                "summary": "John Doe",
                                "self": "https://api.pagerduty.com/users/PUSER123",
                                "html_url": "https://subdomain.pagerduty.com/users/PUSER123",
                            },
                            "channel": {"type": "web_trigger"},
                            "service": {
                                "id": "PSERVICE123",
                                "type": "service_reference",
                                "summary": "My Mail Service",
                            },
                        },
                        {
                            "id": "PLOGENTRY456",
                            "type": "acknowledge_log_entry",
                            "summary": "Acknowledged by John Doe",
                            "self": "https://api.pagerduty.com/log_entries/PLOGENTRY456",
                            "created_at": "2015-10-06T21:35:42Z",
                            "agent": {
                                "id": "PUSER123",
                                "type": "user_reference",
                                "summary": "John Doe",
                            },
                            "channel": {"type": "web"},
                        },
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_log_entry",
                parameters=lambda params: True,
                response={
                    "id": "PLOGENTRY123",
                    "type": "trigger_log_entry",
                    "summary": "Triggered via the website",
                    "self": "https://api.pagerduty.com/log_entries/PLOGENTRY123",
                    "html_url": "https://subdomain.pagerduty.com/incidents/PINCIDENT123/log_entries/PLOGENTRY123",
                    "created_at": "2015-10-06T21:30:42Z",
                    "agent": {
                        "id": "PUSER123",
                        "type": "user_reference",
                        "summary": "John Doe",
                        "self": "https://api.pagerduty.com/users/PUSER123",
                        "html_url": "https://subdomain.pagerduty.com/users/PUSER123",
                    },
                    "channel": {"type": "web_trigger"},
                    "service": {
                        "id": "PSERVICE123",
                        "type": "service_reference",
                        "summary": "My Mail Service",
                    },
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
LOG_ENTRY_COMPETENCY_TESTS = [
    LogEntryCompetencyTest(
        query="Show me all log entries",
        expected_tool_calls=[
            MockToolCall(name="list_log_entries", parameters={"query_model": {}})
        ],
        description="Basic log entry listing (defaults to last 7 days)",
    ),
    LogEntryCompetencyTest(
        query="List log entries",
        expected_tool_calls=[
            MockToolCall(name="list_log_entries", parameters={"query_model": {}})
        ],
        description="Simple log entry listing request",
    ),
    LogEntryCompetencyTest(
        query="Show me log entries from the last 24 hours",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"limit": 100}},
            )
        ],
        description="List log entries with time range (LLM may calculate since timestamp)",
    ),
    LogEntryCompetencyTest(
        query="Get the first 50 log entries",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"limit": 50}},
            )
        ],
        description="List log entries with limit parameter",
    ),
    LogEntryCompetencyTest(
        query="Show me log entries, limit to 25 results",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"limit": 25}},
            )
        ],
        description="List log entries with explicit limit",
    ),
    LogEntryCompetencyTest(
        query="List log entries starting at offset 10",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"offset": 10}},
            )
        ],
        description="List log entries with pagination offset",
    ),
    LogEntryCompetencyTest(
        query="Get log entry PLOGENTRY123",
        expected_tool_calls=[
            MockToolCall(
                name="get_log_entry",
                parameters={"log_entry_id": "PLOGENTRY123"},
            )
        ],
        description="Get specific log entry by ID",
    ),
    LogEntryCompetencyTest(
        query="Show me details of log entry ABC789",
        expected_tool_calls=[
            MockToolCall(
                name="get_log_entry",
                parameters={"log_entry_id": "ABC789"},
            )
        ],
        description="Get specific log entry using natural language",
    ),
    LogEntryCompetencyTest(
        query="What is log entry XYZ456?",
        expected_tool_calls=[
            MockToolCall(
                name="get_log_entry",
                parameters={"log_entry_id": "XYZ456"},
            )
        ],
        description="Get log entry details with question format",
    ),
    LogEntryCompetencyTest(
        query="Show me the next 100 log entries after offset 50",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"limit": 100, "offset": 50}},
            )
        ],
        description="List log entries with both limit and offset for pagination",
    ),
    LogEntryCompetencyTest(
        query="Show me only important log entry changes",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"is_overview": True}},
            )
        ],
        description="List log entries with is_overview filter for important changes only",
    ),
    LogEntryCompetencyTest(
        query="Get log entries with incident details included",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"include": ["incidents"]}},
            )
        ],
        description="List log entries with incidents included",
    ),
    LogEntryCompetencyTest(
        query="Show me log entries for teams TEAM1 and TEAM2",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"team_ids": ["TEAM1", "TEAM2"]}},
            )
        ],
        description="List log entries filtered by team IDs",
    ),
    LogEntryCompetencyTest(
        query="List log entries with services and teams included",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"include": ["services", "teams"]}},
            )
        ],
        description="List log entries with multiple include parameters",
    ),
    LogEntryCompetencyTest(
        query="Get log entries in America/New_York timezone",
        expected_tool_calls=[
            MockToolCall(
                name="list_log_entries",
                parameters={"query_model": {"time_zone": "America/New_York"}},
            )
        ],
        description="List log entries with timezone specification",
    ),
]
