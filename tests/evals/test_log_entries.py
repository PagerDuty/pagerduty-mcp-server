"""Tests for log entry-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class LogEntryCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for log entry-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_log_entries",
            lambda params: True,
            {
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
        )
        mcp.register_mock_response(
            "get_log_entry",
            lambda params: True,
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
        )


# Define the competency test cases
LOG_ENTRY_COMPETENCY_TESTS = [
    LogEntryCompetencyTest(
        query="Show me all log entries",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {}}}],
        description="Basic log entry listing (defaults to last 7 days)",
    ),
    LogEntryCompetencyTest(
        query="List log entries",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {}}}],
        description="Simple log entry listing request",
    ),
    LogEntryCompetencyTest(
        query="Show me log entries from the last 24 hours",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {"limit": 100}}}],
        description="List log entries with time range (LLM may calculate since timestamp)",
    ),
    LogEntryCompetencyTest(
        query="Get the first 50 log entries",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {"limit": 50}}}],
        description="List log entries with limit parameter",
    ),
    LogEntryCompetencyTest(
        query="Show me log entries, limit to 25 results",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {"limit": 25}}}],
        description="List log entries with explicit limit",
    ),
    LogEntryCompetencyTest(
        query="List log entries starting at offset 10",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {"offset": 10}}}],
        description="List log entries with pagination offset",
    ),
    LogEntryCompetencyTest(
        query="Get log entry PLOGENTRY123",
        expected_tools=[{"tool_name": "get_log_entry", "parameters": {"log_entry_id": "PLOGENTRY123"}}],
        description="Get specific log entry by ID",
    ),
    LogEntryCompetencyTest(
        query="Show me details of log entry ABC789",
        expected_tools=[{"tool_name": "get_log_entry", "parameters": {"log_entry_id": "ABC789"}}],
        description="Get specific log entry using natural language",
    ),
    LogEntryCompetencyTest(
        query="What is log entry XYZ456?",
        expected_tools=[{"tool_name": "get_log_entry", "parameters": {"log_entry_id": "XYZ456"}}],
        description="Get log entry details with question format",
    ),
    LogEntryCompetencyTest(
        query="Show me the next 100 log entries after offset 50",
        expected_tools=[{"tool_name": "list_log_entries", "parameters": {"query_model": {"limit": 100, "offset": 50}}}],
        description="List log entries with both limit and offset for pagination",
    ),
]
