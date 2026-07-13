"""Unit tests for alert tools."""

import unittest
from unittest.mock import Mock, patch

from pagerduty_mcp.models import Alert
from pagerduty_mcp.tools.alerts import get_alert_from_incident


class TestAlertTools(unittest.TestCase):
    """Test cases for alert tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_alert_data = {
            "id": "PALERT123",
            "type": "alert",
            "alert_key": "118f19dd-a8a3-4507-abc1-583d310c52cd",
            "summary": "CPU usage over 10%",
            "self": "https://api.pagerduty.com/incidents/PINCIDENT123/alerts/PALERT123",
            "html_url": "https://subdomain.pagerduty.com/alerts/PALERT123",
            "created_at": "2015-10-06T21:30:42Z",
            "status": "triggered",
            "service": {
                "id": "PSERVICE123",
                "type": "service_reference",
                "summary": "My Mail Service",
            },
            "incident": {
                "id": "PINCIDENT123",
                "type": "incident_reference",
            },
        }

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident(self, mock_get_client):
        """Test getting a specific alert from an incident."""
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_alert_data
        mock_get_client.return_value = mock_client

        result = get_alert_from_incident("PINCIDENT123", "PALERT123")

        self.assertIsInstance(result, Alert)
        self.assertEqual(result.id, "PALERT123")
        mock_client.rget.assert_called_once_with("/incidents/PINCIDENT123/alerts/PALERT123")

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_empty_alert_id(self, mock_get_client):
        """Test that an empty alert_id is rejected before any API call.

        An empty alert_id would otherwise produce a request to
        /incidents/{incident_id}/alerts/ (trailing slash), which the API
        rejects with a 404.
        """
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_alert_from_incident("PINCIDENT123", "")

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_blank_alert_id(self, mock_get_client):
        """Test that a whitespace-only alert_id is rejected before any API call."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_alert_from_incident("PINCIDENT123", "   ")

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_quoted_empty_alert_id(self, mock_get_client):
        """Test that a literal quoted-empty alert_id ('""' or "''") is rejected.

        Clients sometimes serialize an empty string as two literal quote
        characters, which would otherwise be sent as /alerts/%22%22 and 404.
        """
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        for quoted_empty in ('""', "''"):
            with self.assertRaises(ValueError):
                get_alert_from_incident("PINCIDENT123", quoted_empty)

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_quoted_empty_incident_id(self, mock_get_client):
        """Test that a literal quoted-empty incident_id is rejected before any API call."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_alert_from_incident('""', "PALERT123")

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_invisible_unicode_alert_id(self, mock_get_client):
        """Test that invisible-unicode-only alert_ids are rejected before any API call."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        for invisible in ("\u200b", "\u200d", "\ufeff", "\u200b\u200b"):
            with self.assertRaises(ValueError):
                get_alert_from_incident("PINCIDENT123", invisible)

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_typographic_quotes_alert_id(self, mock_get_client):
        """Test that curly-quote/backtick-only alert_ids are rejected before any API call."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        for quoted_empty in ("\u201c\u201d", "\u2018\u2019", "``", '\\"\\"'):
            with self.assertRaises(ValueError):
                get_alert_from_incident("PINCIDENT123", quoted_empty)

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_null_literal_alert_id(self, mock_get_client):
        """Test that null-like literal alert_ids are rejected before any API call.

        LLM-driven clients sometimes serialize a missing value as the literal
        string "null"/"None"/"undefined"/"nil"; none of these can ever be a
        valid PagerDuty ID.
        """
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        for null_literal in ("null", "NULL", "None", "undefined", "nil", '"null"'):
            with self.assertRaises(ValueError):
                get_alert_from_incident("PINCIDENT123", null_literal)

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_null_literal_incident_id(self, mock_get_client):
        """Test that a null-like literal incident_id is rejected before any API call."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_alert_from_incident("null", "PALERT123")

        mock_client.rget.assert_not_called()

    @patch("pagerduty_mcp.tools.alerts.get_client")
    def test_get_alert_from_incident_empty_incident_id(self, mock_get_client):
        """Test that an empty incident_id is rejected before any API call."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_alert_from_incident("", "PALERT123")

        mock_client.rget.assert_not_called()


if __name__ == "__main__":
    unittest.main()
