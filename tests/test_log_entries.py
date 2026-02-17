"""Unit tests for log entry tools."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from pagerduty_mcp.models import ListResponseModel, LogEntry, LogEntryQuery
from pagerduty_mcp.tools.log_entries import get_log_entry, list_log_entries


class TestLogEntryTools(unittest.TestCase):
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

    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_get_log_entry(self, mock_get_client):
        """Test getting a specific log entry."""
        # Arrange
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_log_entry_data
        mock_get_client.return_value = mock_client

        # Act
        result = get_log_entry("PLOGENTRY123")

        # Assert
        self.assertIsInstance(result, LogEntry)
        self.assertEqual(result.id, "PLOGENTRY123")
        self.assertEqual(result.type, "trigger_log_entry")
        self.assertEqual(result.summary, "Triggered via the website")
        mock_client.rget.assert_called_once_with("/log_entries/PLOGENTRY123")

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries(self, mock_get_client, mock_paginate):
        """Test listing log entries with default time range (last 7 days)."""
        # Arrange
        mock_client = Mock()
        mock_get_client.return_value = mock_client
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
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_with_time_filter(self, mock_get_client, mock_paginate):
        """Test listing log entries with time range filter."""
        # Arrange
        mock_client = Mock()
        mock_get_client.return_value = mock_client
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
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_empty_result(self, mock_get_client, mock_paginate):
        """Test listing log entries when no entries exist."""
        # Arrange
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = []

        query_model = LogEntryQuery()

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_with_empty_string_timestamps(self, mock_get_client, mock_paginate):
        """Test that empty string timestamps are converted to None and then to defaults."""
        # Arrange
        mock_client = Mock()
        mock_get_client.return_value = mock_client
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
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_with_pagination(self, mock_get_client, mock_paginate):
        """Test listing log entries with pagination parameters."""
        # Arrange
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = [self.sample_log_entry_data]

        query_model = LogEntryQuery(limit=25, offset=10)

        # Act
        result = list_log_entries(query_model)

        # Assert
        self.assertIsInstance(result, ListResponseModel)

    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_get_log_entry_with_channel_without_type(self, mock_get_client):
        """Test getting a log entry where channel doesn't have a type field."""
        # Arrange
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_service_change_log_entry
        mock_get_client.return_value = mock_client

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
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_mixed_channel_types(self, mock_get_client, mock_paginate):
        """Test listing log entries with different channel structures."""
        # Arrange
        mock_client = Mock()
        mock_get_client.return_value = mock_client
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

    def test_log_entry_query_with_is_overview(self):
        """Test LogEntryQuery with is_overview parameter."""
        query = LogEntryQuery(is_overview=True)
        params = query.to_params()

        self.assertTrue("is_overview" in params)
        self.assertTrue(params["is_overview"])

    def test_log_entry_query_with_include(self):
        """Test LogEntryQuery with include parameter."""
        query = LogEntryQuery(include=["incidents", "services", "teams"])
        params = query.to_params()

        self.assertIn("include[]", params)
        self.assertEqual(params["include[]"], ["incidents", "services", "teams"])

    def test_log_entry_query_with_team_ids(self):
        """Test LogEntryQuery with team_ids filter."""
        query = LogEntryQuery(team_ids=["TEAM1", "TEAM2"])
        params = query.to_params()

        self.assertIn("team_ids[]", params)
        self.assertEqual(params["team_ids[]"], ["TEAM1", "TEAM2"])

    def test_log_entry_query_with_time_zone(self):
        """Test LogEntryQuery with time_zone parameter."""
        query = LogEntryQuery(time_zone="America/New_York")
        params = query.to_params()

        self.assertIn("time_zone", params)
        self.assertEqual(params["time_zone"], "America/New_York")

    def test_log_entry_query_with_total(self):
        """Test LogEntryQuery with total parameter."""
        query = LogEntryQuery(total=True)
        params = query.to_params()

        self.assertIn("total", params)
        self.assertTrue(params["total"])

    def test_log_entry_query_with_all_filters(self):
        """Test LogEntryQuery with all filter parameters."""
        since_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        until_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

        query = LogEntryQuery(
            since=since_date,
            until=until_date,
            limit=50,
            offset=10,
            is_overview=True,
            include=["incidents", "teams"],
            team_ids=["TEAM1"],
            time_zone="UTC",
            total=True,
        )
        params = query.to_params()

        self.assertEqual(params["since"], since_date.isoformat())
        self.assertEqual(params["until"], until_date.isoformat())
        self.assertEqual(params["limit"], 50)
        self.assertEqual(params["offset"], 10)
        self.assertTrue(params["is_overview"])
        self.assertEqual(params["include[]"], ["incidents", "teams"])
        self.assertEqual(params["team_ids[]"], ["TEAM1"])
        self.assertEqual(params["time_zone"], "UTC")
        self.assertTrue(params["total"])


if __name__ == "__main__":
    unittest.main()
