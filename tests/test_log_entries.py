"""Unit tests for log entry tools."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from tests.context_test_case import ContextTestCase
from pagerduty_mcp.models import ListResponseModel, LogEntry, LogEntryQuery
from pagerduty_mcp.tools.log_entries import get_log_entry, list_log_entries


class TestLogEntryTools(ContextTestCase):
    """Test cases for log entry tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_log_entry_data = {
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
                "self": "https://api.pagerduty.com/services/PSERVICE123",
                "html_url": "https://subdomain.pagerduty.com/service-directory/PSERVICE123",
            },
            "incident": {
                "id": "PINCIDENT123",
                "type": "incident_reference",
                "summary": "[#1234] The server is on fire.",
                "self": "https://api.pagerduty.com/incidents/PINCIDENT123",
                "html_url": "https://subdomain.pagerduty.com/incidents/PINCIDENT123",
            },
            "teams": [
                {
                    "id": "PTEAM123",
                    "type": "team_reference",
                    "summary": "Engineering",
                    "self": "https://api.pagerduty.com/teams/PTEAM123",
                    "html_url": "https://subdomain.pagerduty.com/teams/PTEAM123",
                }
            ],
        }

        # Sample log entry with channel without type (service change log entry)
        cls.sample_service_change_log_entry = {
            "id": "PLOGENTRY456",
            "type": "service_change_log_entry",
            "summary": "Service changed",
            "self": "https://api.pagerduty.com/log_entries/PLOGENTRY456",
            "created_at": "2015-10-06T21:30:42Z",
            "agent": {
                "id": "PUSER123",
                "type": "user_reference",
                "summary": "John Doe",
            },
            "channel": {
                "old_service": {
                    "id": "PSERVICE123",
                    "type": "service_reference",
                }
            },
            "service": {
                "id": "PSERVICE456",
                "type": "service_reference",
            },
        }

    def test_get_log_entry(self):
        """Test getting a specific log entry."""
        # Arrange
        self.mock_client.rget.return_value = self.sample_log_entry_data

        # Act
        result = get_log_entry("PLOGENTRY123")

        # Assert
        self.assertIsInstance(result, LogEntry)
        self.assertEqual(result.id, "PLOGENTRY123")
        self.assertEqual(result.type, "trigger_log_entry")
        self.assertEqual(result.summary, "Triggered via the website")
        self.mock_client.rget.assert_called_once_with("/log_entries/PLOGENTRY123")

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    def test_list_log_entries(self, mock_paginate):
        """Test listing log entries with default time range (last 7 days)."""
        # Arrange
        mock_paginate.return_value = [self.sample_log_entry_data]

        query_model = LogEntryQuery()

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], LogEntry)
        self.assertEqual(result.response[0].id, "PLOGENTRY123")
        mock_paginate.assert_called_once()

        # Verify that default timestamps were set (last 7 days)
        self.assertIsNotNone(query_model.since)
        self.assertIsNotNone(query_model.until)

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    def test_list_log_entries_with_time_filter(self, mock_paginate):
        """Test listing log entries with time range filter."""
        # Arrange
        mock_paginate.return_value = [self.sample_log_entry_data, self.sample_log_entry_data]

        since = datetime.now() - timedelta(days=7)
        until = datetime.now()
        query_model = LogEntryQuery(since=since, until=until, limit=50)

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 2)

        # Verify paginate was called with proper parameters
        call_args = mock_paginate.call_args
        self.assertEqual(call_args.kwargs["entity"], "log_entries")
        self.assertEqual(call_args.kwargs["maximum_records"], 50)

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    def test_list_log_entries_empty_result(self, mock_paginate):
        """Test listing log entries when no entries exist."""
        # Arrange
        mock_paginate.return_value = []

        query_model = LogEntryQuery()

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    def test_list_log_entries_with_empty_string_timestamps(self, mock_paginate):
        """Test that empty string timestamps are converted to None and then to defaults."""
        # Arrange
        mock_paginate.return_value = [self.sample_log_entry_data]

        # Create query with empty strings (simulating MCP interface behavior)
        query_model = LogEntryQuery(since="", until="")

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)

        # Verify that empty strings were converted to None and then to default values
        self.assertIsNotNone(query_model.since)
        self.assertIsNotNone(query_model.until)

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    def test_list_log_entries_with_limit_offset(self, mock_paginate):
        """Test listing log entries with limit and offset."""
        # Arrange
        mock_paginate.return_value = [self.sample_log_entry_data]

        query_model = LogEntryQuery(limit=25, offset=10)

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)

    def test_get_log_entry_with_channel_without_type(self):
        """Test getting a log entry where channel doesn't have a type field."""
        # Arrange
        self.mock_client.rget.return_value = self.sample_service_change_log_entry

        # Act
        result = get_log_entry("PLOGENTRY456")

        # Assert
        self.assertIsInstance(result, LogEntry)
        self.assertEqual(result.id, "PLOGENTRY456")
        self.assertEqual(result.type, "service_change_log_entry")
        self.assertIsNotNone(result.channel)
        # Channel type should be None for this log entry type
        self.assertIsNone(result.channel.type)

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    def test_list_log_entries_mixed_channel_types(self, mock_paginate):
        """Test listing log entries with different channel structures."""
        # Arrange
        # Mix different log entry types with different channel structures
        mock_paginate.return_value = [
            self.sample_log_entry_data,
            self.sample_service_change_log_entry,
        ]

        query_model = LogEntryQuery()

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 2)
        # First entry should have channel type
        self.assertEqual(result.response[0].channel.type, "web_trigger")
        # Second entry should have channel without type
        self.assertIsNone(result.response[1].channel.type)

    def test_log_entry_query_to_params(self):
        """Test LogEntryQuery to_params conversion."""
        # Test with all parameters
        since = datetime(2023, 1, 1, 0, 0, 0)
        until = datetime(2023, 12, 31, 23, 59, 59)
        query = LogEntryQuery(since=since, until=until, limit=50, offset=10)
        params = query.to_params()

        self.assertEqual(params["since"], since.isoformat())
        self.assertEqual(params["until"], until.isoformat())
        self.assertEqual(params["limit"], 50)
        self.assertEqual(params["offset"], 10)

    def test_log_entry_query_to_params_partial(self):
        """Test LogEntryQuery to_params with only some parameters."""
        # Test with only since parameter
        since = datetime(2023, 1, 1, 0, 0, 0)
        query = LogEntryQuery(since=since)
        params = query.to_params()

        self.assertEqual(params["since"], since.isoformat())
        self.assertNotIn("until", params)
        self.assertEqual(params["limit"], 100)  # default
        self.assertEqual(params["offset"], 0)  # default

    def test_log_entry_query_defaults(self):
        """Test LogEntryQuery default values."""
        query = LogEntryQuery()

        self.assertIsNone(query.since)
        self.assertIsNone(query.until)
        self.assertEqual(query.limit, 100)
        self.assertEqual(query.offset, 0)

    def test_log_entry_query_empty_string_validator(self):
        """Test that LogEntryQuery properly handles empty strings."""
        # Empty strings should be converted to None
        query = LogEntryQuery(since="", until="")

        self.assertIsNone(query.since)
        self.assertIsNone(query.until)


if __name__ == "__main__":
    unittest.main()
