from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from pagerduty_mcp.models.alerts import Alert, AlertQuery
from pagerduty_mcp.models.references import ServiceReference
from pagerduty_mcp.tools.alerts import get_alert, list_alerts, list_incident_alerts


class TestAlertTools:
    def test_list_incident_alerts_success(self):
        """Test successful incident alerts retrieval."""
        mock_alert_data = {
            "id": "PALERT1",
            "summary": "Test alert",
            "status": "triggered",
            "severity": "error",
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-01T10:05:00Z",
            "service": {"id": "PSERVICE1", "type": "service_reference", "summary": "Test Service"},
        }

        with patch("pagerduty_mcp.tools.alerts.paginate") as mock_paginate:
            mock_paginate.return_value = [mock_alert_data]

            result = list_incident_alerts("PINCIDENT1")

            mock_paginate.assert_called_once()
            assert len(result.response) == 1
            assert result.response[0].id == "PALERT1"
            assert result.response[0].summary == "Test alert"

    def test_list_incident_alerts_empty(self):
        """Test incident with no alerts."""
        with patch("pagerduty_mcp.tools.alerts.paginate") as mock_paginate:
            mock_paginate.return_value = []

            result = list_incident_alerts("PINCIDENT2")

            assert len(result.response) == 0
            assert result.response == []

    def test_list_alerts_with_filters(self):
        """Test alert search with filters."""
        mock_alert_data = {
            "id": "PALERT2",
            "summary": "Critical alert",
            "status": "acknowledged",
            "severity": "critical",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:05:00Z",
            "service": {"id": "PSERVICE2", "type": "service_reference", "summary": "Critical Service"},
        }

        query = AlertQuery(
            statuses=["acknowledged"],
            severities=["critical"],
            service_ids=["PSERVICE2"],
            limit=50,
        )

        with patch("pagerduty_mcp.tools.alerts.paginate") as mock_paginate:
            mock_paginate.return_value = [mock_alert_data]

            result = list_alerts(query)

            mock_paginate.assert_called_once()
            call_args = mock_paginate.call_args
            assert call_args[1]["entity"] == "alerts"
            assert call_args[1]["maximum_records"] == 50

            assert len(result.response) == 1
            assert result.response[0].severity == "critical"

    def test_list_alerts_no_filters(self):
        """Test alert search with no filters."""
        query = AlertQuery()

        with patch("pagerduty_mcp.tools.alerts.paginate") as mock_paginate:
            mock_paginate.return_value = []

            result = list_alerts(query)

            call_args = mock_paginate.call_args
            assert call_args[1]["maximum_records"] == 100  # default limit

    def test_get_alert_success(self):
        """Test successful alert retrieval."""
        mock_alert_data = {
            "id": "PALERT3",
            "summary": "Detailed alert",
            "status": "resolved",
            "severity": "warning",
            "alert_key": "test-key-123",
            "created_at": "2023-01-01T14:00:00Z",
            "updated_at": "2023-01-01T14:10:00Z",
            "resolved_at": "2023-01-01T14:15:00Z",
            "service": {"id": "PSERVICE3", "type": "service_reference", "summary": "Warning Service"},
            "incident": {"id": "PINCIDENT3", "type": "incident_reference", "summary": "Related Incident"},
            "integration": {"id": "PINT3", "type": "integration_reference", "summary": "Monitoring Tool"},
            "body": {"type": "alert_body", "details": "Detailed information about the alert"},
        }

        with patch("pagerduty_mcp.tools.alerts.get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.rget.return_value = mock_alert_data
            mock_get_client.return_value = mock_client

            result = get_alert("PALERT3")

            mock_client.rget.assert_called_once_with("/alerts/PALERT3")
            assert result.id == "PALERT3"
            assert result.alert_key == "test-key-123"
            assert result.status == "resolved"
            assert result.incident.id == "PINCIDENT3"
            assert result.integration.id == "PINT3"
            assert result.body.details == "Detailed information about the alert"

    def test_get_alert_not_found(self):
        """Test alert not found error handling."""
        with patch("pagerduty_mcp.tools.alerts.get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.rget.side_effect = Exception("Alert not found")
            mock_get_client.return_value = mock_client

            with pytest.raises(Exception, match="Alert not found"):
                get_alert("INVALID_ALERT")

    def test_alert_query_parameter_conversion(self):
        """Test that AlertQuery parameters are correctly passed to paginate."""
        query = AlertQuery(
            service_ids=["SERV1", "SERV2"],
            statuses=["triggered"],
            since=datetime(2023, 1, 1),
            until=datetime(2023, 1, 2),
        )

        with patch("pagerduty_mcp.tools.alerts.paginate") as mock_paginate:
            mock_paginate.return_value = []

            list_alerts(query)

            call_args = mock_paginate.call_args
            params = call_args[1]["params"]

            assert params["service_ids[]"] == ["SERV1", "SERV2"]
            assert params["statuses[]"] == ["triggered"]
            assert "since" in params
            assert "until" in params