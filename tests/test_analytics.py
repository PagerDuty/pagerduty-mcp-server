"""Unit tests for analytics tools."""

import json
import unittest
from unittest.mock import Mock, patch

from pagerduty_mcp.models.analytics import (
    AnalyticsIncidentFilters,
    AnalyticsFilters,
    GetIncidentMetricsByServiceRequest,
    GetIncidentMetricsByTeamRequest,
    GetResponderLoadMetricsRequest,
)
from pagerduty_mcp.tools.analytics import (
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
)


class TestGetIncidentMetricsByService(unittest.TestCase):
    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_returns_json_list(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "data": [
                {
                    "service_id": "SVC1",
                    "service_name": "API",
                    "total_incident_count": 10,
                    "mean_seconds_to_first_ack": 120,
                    "mean_seconds_to_resolve": 600,
                    "total_escalation_count": 2,
                    "total_incidents_manual_escalated": 1,
                    "total_interruptions": 5,
                    "up_time_pct": 99.5,
                }
            ]
        }
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByServiceRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_service(request)

        data = json.loads(result)
        self.assertEqual(len(data["response"]), 1)
        self.assertEqual(data["response"][0]["service_name"], "API")
        self.assertEqual(data["response"][0]["total_incident_count"], 10)
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/services",
            json={
                "filters": {
                    "created_at_start": "2026-03-01T00:00:00Z",
                    "created_at_end": "2026-04-01T00:00:00Z",
                }
            },
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_handles_empty_response(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByServiceRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_service(request)

        data = json.loads(result)
        self.assertEqual(data["response"], [])


class TestGetIncidentMetricsByTeam(unittest.TestCase):
    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_returns_json_list(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "data": [
                {
                    "team_id": "T1",
                    "team_name": "Platform",
                    "total_incident_count": 5,
                    "mean_seconds_to_first_ack": 90,
                    "mean_seconds_to_resolve": 300,
                    "total_escalation_count": 1,
                    "total_incidents_manual_escalated": 0,
                    "total_interruptions": 3,
                    "up_time_pct": 99.9,
                }
            ]
        }
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByTeamRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_team(request)

        data = json.loads(result)
        self.assertEqual(data["response"][0]["team_name"], "Platform")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/teams",
            json={
                "filters": {
                    "created_at_start": "2026-03-01T00:00:00Z",
                    "created_at_end": "2026-04-01T00:00:00Z",
                }
            },
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_handles_empty_response(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByTeamRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_team(request)

        data = json.loads(result)
        self.assertEqual(data["response"], [])


class TestGetResponderLoadMetrics(unittest.TestCase):
    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_returns_json_list(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "data": [
                {
                    "responder_id": "U1",
                    "responder_name": "Alice",
                    "total_seconds_on_call": 86400,
                    "total_incident_count": 3,
                    "total_incidents_acknowledged": 3,
                    "total_sleep_hour_interruptions": 1,
                    "total_engaged_seconds": 3600,
                    "mean_time_to_acknowledge_seconds": 45,
                }
            ]
        }
        mock_get_client.return_value = mock_client

        request = GetResponderLoadMetricsRequest(
            filters=AnalyticsFilters(
                date_range_start="2026-03-01T00:00:00Z",
                date_range_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_responder_load_metrics(request)

        data = json.loads(result)
        self.assertEqual(data["response"][0]["responder_name"], "Alice")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/responders/all",
            json={
                "filters": {
                    "date_range_start": "2026-03-01T00:00:00Z",
                    "date_range_end": "2026-04-01T00:00:00Z",
                }
            },
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_handles_empty_response(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetResponderLoadMetricsRequest(
            filters=AnalyticsFilters(
                date_range_start="2026-03-01T00:00:00Z",
                date_range_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_responder_load_metrics(request)

        data = json.loads(result)
        self.assertEqual(data["response"], [])
