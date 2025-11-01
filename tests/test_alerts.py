"""Unit tests for alert tools."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from pagerduty_mcp.models import Alert, AlertQuery, ListResponseModel
from pagerduty_mcp.tools.alerts import get_alert, list_alerts


class TestAlertTools(unittest.TestCase):
    """Test cases for alert tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_alert_data = {
            "id": "PALERT123",
            "summary": "Test Alert",
            "status": "triggered",
            "severity": "critical",
            "created_at": "2023-06-15T14:30:00Z",
            "resolved_at": None,
            "service": {
                "id": "PSERVICE123",
                "type": "service_reference",
                "summary": "Test Service",
                "html_url": "https://test.pagerduty.com/services/PSERVICE123",
            },
            "html_url": "https://test.pagerduty.com/alerts/PALERT123",
            "incident": {
                "id": "PINCIDENT123",
                "type": "incident_reference",
                "summary": "Test Incident",
                "html_url": "https://test.pagerduty.com/incidents/PINCIDENT123",
            },
            "body": {
                "type": "alert_body",
                "details": "Test alert details",
            },
            "first_trigger_log_entry": {
                "id": "PLOGENTRY123",
                "type": "trigger_log_entry",
                "summary": "Alert triggered",
            },
        }

        cls.sample_alert_list_response = {
            "alerts": [cls.sample_alert_data],
            "limit": 25,
            "offset": 0,
            "total": 1,
            "more": False,
        }

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_success(self, mock_get_client):
        """Test successful alert retrieval for an incident."""
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_alert_data
        mock_get_client.return_value = mock_client

        result = get_alert("PINCIDENT123", "PALERT123")

        self.assertIsInstance(result, Alert)
        self.assertEqual(result.id, "PALERT123")
        self.assertEqual(result.summary, "Test Alert")
        self.assertEqual(result.status, "triggered")
        self.assertEqual(result.severity, "critical")
        self.assertIsNotNone(result.first_trigger_log_entry)
        self.assertEqual(result.first_trigger_log_entry["id"], "PLOGENTRY123")
        self.assertEqual(result.first_trigger_log_entry["type"], "trigger_log_entry")
        mock_client.rget.assert_called_once_with("/incidents/PINCIDENT123/alerts/PALERT123")

    @patch("pagerduty_mcp.tools.alerts.paginate")
    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_list_alerts_success(self, mock_get_client, mock_paginate):
        """Test successful alert listing for an incident."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = [self.sample_alert_data]

        query = AlertQuery(status=["triggered"], limit=25)
        result = list_alerts("PINCIDENT123", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], Alert)
        self.assertEqual(result.response[0].id, "PALERT123")

        mock_paginate.assert_called_once_with(
            client=mock_client,
            entity="incidents/PINCIDENT123/alerts",
            params={"statuses[]": ["triggered"]},
            maximum_records=25,
        )

    @patch("pagerduty_mcp.tools.alerts.paginate")
    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_list_alerts_with_filters(self, mock_get_client, mock_paginate):
        """Test alert listing with multiple filters for an incident."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = [self.sample_alert_data]

        since_date = datetime(2023, 6, 1, 0, 0, 0)
        until_date = datetime(2023, 6, 30, 23, 59, 59)

        query = AlertQuery(
            status=["triggered", "resolved"],
            severity=["critical", "error"],
            since=since_date,
            until=until_date,
            service_ids=["PSERVICE123"],
            limit=50,
        )

        list_alerts("PINCIDENT123", query)

        expected_params = {
            "statuses[]": ["triggered", "resolved"],
            "severities[]": ["critical", "error"],
            "since": since_date.isoformat(),
            "until": until_date.isoformat(),
            "service_ids[]": ["PSERVICE123"],
        }

        mock_paginate.assert_called_once_with(
            client=mock_client,
            entity="incidents/PINCIDENT123/alerts",
            params=expected_params,
            maximum_records=50,
        )

    @patch("pagerduty_mcp.tools.alerts.paginate")
    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_list_alerts_empty_result(self, mock_get_client, mock_paginate):
        """Test alert listing with empty results."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_paginate.return_value = []

        query = AlertQuery(status=["resolved"])
        result = list_alerts("PINCIDENT123", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 0)

    def test_alert_query_to_params(self):
        """Test AlertQuery to_params method."""
        since_date = datetime(2023, 6, 1, 0, 0, 0)
        until_date = datetime(2023, 6, 30, 23, 59, 59)

        query = AlertQuery(
            status=["triggered"],
            severity=["critical"],
            since=since_date,
            until=until_date,
            service_ids=["PSERVICE123"],
            sort_by=["created_at:desc"],
        )

        params = query.to_params()

        expected_params = {
            "statuses[]": ["triggered"],
            "severities[]": ["critical"],
            "since": since_date.isoformat(),
            "until": until_date.isoformat(),
            "service_ids[]": ["PSERVICE123"],
            "sort_by": "created_at:desc",
        }

        self.assertEqual(params, expected_params)

    def test_alert_query_empty_params(self):
        """Test AlertQuery with no filters."""
        query = AlertQuery()
        params = query.to_params()
        self.assertEqual(params, {})


if __name__ == "__main__":
    unittest.main()

