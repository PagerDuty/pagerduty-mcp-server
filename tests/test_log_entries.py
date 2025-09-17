"""Unit tests for log_entries tools."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from pagerduty_mcp.models import GetLogEntriesQuery, ListResponseModel, LogEntries, LogEntriesQuery
from pagerduty_mcp.tools.log_entries import get_log_entry, list_log_entries


class TestLogEntryTools(unittest.TestCase):
    """Test cases for log entry tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_log_entries_data = {
            "id": "R123ABC",
            "summary": "Triggered through email.",
            "created_at": "2025-08-29T17:49:21Z",
            "html_url": "https://test.pagerduty.com/incidents/PINCIDENT123/log_entries/R123ABC",
            "incident": {
                "id": "PINCIDENT123",
                "type": "incident_reference",
                "summary": "[#123] CRITICAL : Alert fired",
                "self": "https://api.pagerduty.com/incidents/PINCIDENT123",
                "html_url": "https://test.pagerduty.com/incidents/PINCIDENT123",
            },
            "teams": [
                {
                    "id": "TEAM123",
                    "type": "team_reference",
                    "summary": "Engineering Team",
                    "self": "https://api.pagerduty.com/teams/TEAM123",
                    "html_url": "https://test.pagerduty.com/teams/TEAM123",
                }
            ],
            "service": {"id": "SVC123", "summary": "Test Service", "type": "service_reference"},
            "channel": {
                "type": "email",
                "summary": "[#123] CRITICAL : Alert fired",
                "body": "Sample email body",
                "body_content_type": "text/html",
                "details": {},
                "html_url": "/incidents/PINCIDENT123/log_entries/R123ABC/show_html_details",
            },
            "type": "log_entries",
        }

        cls.sample_log_entries_list_response = {
            "log_entries": [cls.sample_log_entries_data],
            "limit": 25,
            "offset": 0,
            "total": 1,
            "more": False,
        }

    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_get_log_entry_success(self, mock_get_client):
        """Test successful log_entry retrieval."""
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_log_entries_data
        mock_get_client.return_value = mock_client

        result = get_log_entry("R123ABC", query_model=GetLogEntriesQuery(include=["channels"]))

        self.assertIsInstance(result, LogEntries)
        self.assertEqual(result.id, "R123ABC")
        self.assertEqual(result.summary, "Triggered through email.")
        mock_client.rget.assert_called_once_with("/log_entries/R123ABC", params={"include[]": ["channels"]})

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_success(self, mock_get_client, mock_paginate):
        """Test successful log_entries listing."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = [self.sample_log_entries_data]

        query = LogEntriesQuery(include=["channels"], limit=25)
        result = list_log_entries(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], LogEntries)
        self.assertEqual(result.response[0].id, "R123ABC")

        mock_paginate.assert_called_once_with(
            client=mock_client,
            entity="log_entries",
            params={"include[]": ["channels"]},
            maximum_records=25,
        )

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_with_filters(self, mock_get_client, mock_paginate):
        """Test log_entries listing with multiple filters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = [self.sample_log_entries_data]

        since_date = datetime(2023, 6, 1, 0, 0, 0)
        until_date = datetime(2023, 6, 30, 23, 59, 59)

        query = LogEntriesQuery(
            include=["channels", "services"],
            since=since_date,
            until=until_date,
            team_ids=["TEAM123"],
            limit=50,
        )

        list_log_entries(query)

        expected_params = {
            "include[]": ["channels", "services"],
            "since": since_date.isoformat(),
            "until": until_date.isoformat(),
            "team_ids[]": ["TEAM123"],
        }

        mock_paginate.assert_called_once_with(
            client=mock_client,
            entity="log_entries",
            params=expected_params,
            maximum_records=50,
        )

    @patch("pagerduty_mcp.tools.log_entries.paginate")
    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_list_log_entries_empty_result(self, mock_get_client, mock_paginate):
        """Test log_entries listing with empty results."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = []

        query = LogEntriesQuery(include=["channels"])
        result = list_log_entries(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 0)

    def test_log_entries_query_to_params(self):
        """Test LogEntriesQuery to_params method."""
        since_date = datetime(2023, 6, 1, 0, 0, 0)
        until_date = datetime(2023, 6, 30, 23, 59, 59)

        query = LogEntriesQuery(
            include=["channels", "services"],
            since=since_date,
            until=until_date,
            team_ids=["TEAM123"],
            sort_by=["created_at:desc"],
        )

        params = query.to_params()

        expected_params = {
            "include[]": ["channels", "services"],
            "since": since_date.isoformat(),
            "until": until_date.isoformat(),
            "team_ids[]": ["TEAM123"],
            "sort_by": "created_at:desc",
        }

        self.assertEqual(params, expected_params)

    def test_log_entries_query_empty_params(self):
        """Test LogEntriesQuery with no filters."""
        query = LogEntriesQuery()
        params = query.to_params()
        self.assertEqual(params, {})


if __name__ == "__main__":
    unittest.main()
