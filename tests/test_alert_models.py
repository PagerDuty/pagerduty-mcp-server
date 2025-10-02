from datetime import datetime

import pytest

from pagerduty_mcp.models.alerts import Alert, AlertBody, AlertQuery, AlertSeverity, AlertStatus
from pagerduty_mcp.models.references import IncidentReference, IntegrationReference, ServiceReference


class TestAlertModels:
    def test_alert_model_validation(self):
        """Test Alert model validation with required fields."""
        service_ref = ServiceReference(id="PSERVICE1", summary="Test Service")

        alert = Alert(
            id="PALERT1",
            summary="Test alert",
            status="triggered",
            severity="error",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            service=service_ref,
        )

        assert alert.id == "PALERT1"
        assert alert.summary == "Test alert"
        assert alert.status == "triggered"
        assert alert.severity == "error"
        assert alert.type == "alert"
        assert alert.service.id == "PSERVICE1"

    def test_alert_model_with_relationships(self):
        """Test Alert model with optional relationship fields."""
        service_ref = ServiceReference(id="PSERVICE1", summary="Test Service")
        incident_ref = IncidentReference(id="PINCIDENT1", summary="Test Incident")
        integration_ref = IntegrationReference(id="PINTEGRATION1", summary="Test Integration")
        alert_body = AlertBody(details="Detailed alert information")

        alert = Alert(
            id="PALERT1",
            summary="Test alert",
            status="acknowledged",
            severity="critical",
            alert_key="test-alert-key",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=datetime.now(),
            service=service_ref,
            incident=incident_ref,
            integration=integration_ref,
            body=alert_body,
        )

        assert alert.incident.id == "PINCIDENT1"
        assert alert.integration.id == "PINTEGRATION1"
        assert alert.body.details == "Detailed alert information"
        assert alert.alert_key == "test-alert-key"

    def test_alert_query_to_params(self):
        """Test AlertQuery parameter conversion."""
        query = AlertQuery(
            service_ids=["PSERVICE1", "PSERVICE2"],
            since=datetime(2023, 1, 1, 10, 0, 0),
            until=datetime(2023, 1, 2, 10, 0, 0),
            statuses=["triggered", "acknowledged"],
            severities=["error", "critical"],
            limit=50,
        )

        params = query.to_params()

        assert params["service_ids[]"] == ["PSERVICE1", "PSERVICE2"]
        assert params["since"] == "2023-01-01T10:00:00"
        assert params["until"] == "2023-01-02T10:00:00"
        assert params["statuses[]"] == ["triggered", "acknowledged"]
        assert params["severities[]"] == ["error", "critical"]

    def test_alert_query_empty_filters(self):
        """Test AlertQuery with no filters."""
        query = AlertQuery()
        params = query.to_params()

        assert params == {}
        assert query.limit == 100  # default limit

    def test_alert_body_type(self):
        """Test AlertBody model type property."""
        body = AlertBody(details="Test alert details")

        assert body.type == "alert_body"
        assert body.details == "Test alert details"

    def test_alert_status_literal(self):
        """Test AlertStatus literal values."""
        valid_statuses = ["triggered", "acknowledged", "resolved", "suppressed"]

        for status in valid_statuses:
            alert = Alert(
                id="PALERT1",
                summary="Test alert",
                status=status,
                severity="error",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                service=ServiceReference(id="PSERVICE1"),
            )
            assert alert.status == status

    def test_alert_severity_literal(self):
        """Test AlertSeverity literal values."""
        valid_severities = ["critical", "error", "warning", "info"]

        for severity in valid_severities:
            alert = Alert(
                id="PALERT1",
                summary="Test alert",
                status="triggered",
                severity=severity,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                service=ServiceReference(id="PSERVICE1"),
            )
            assert alert.severity == severity