import json
import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.analytics import (
    AnalyticsAggregatedMetrics,
    AnalyticsFilters,
    AnalyticsIncidentFilters,
    AnalyticsResponderLoad,
    AnalyticsResponderMetrics,
    AnalyticsServiceMetrics,
    AnalyticsTeamMetrics,
    GetIncidentMetricsAllRequest,
    GetIncidentMetricsByServiceRequest,
    GetIncidentMetricsByTeamRequest,
    GetResponderLoadMetricsRequest,
    GetResponderMetricsRequest,
)
from pagerduty_mcp.tools.analytics import (
    get_incident_metrics_all,
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_responder_metrics,
)


class TestAnalyticsTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.responder_filters = AnalyticsFilters(
            date_range_start="2026-01-01T00:00:00Z",
            date_range_end="2026-01-31T23:59:59Z",
        )
        cls.incident_filters = AnalyticsIncidentFilters(
            created_at_start="2026-01-01T00:00:00Z",
            created_at_end="2026-01-31T23:59:59Z",
        )
        cls.sample_responder_data = [
            {
                "responder_id": "USER1",
                "responder_name": "Alice",
                "team_id": "TEAM1",
                "team_name": "Eng",
                "total_seconds_on_call": 86400,
                "total_interruptions": 5,
                "total_business_hour_interruptions": 2,
                "total_off_hour_interruptions": 2,
                "total_sleep_hour_interruptions": 1,
            }
        ]
        cls.sample_service_data = [
            {
                "service_id": "SVC1",
                "service_name": "Web",
                "total_incident_count": 10,
                "mean_seconds_to_first_ack": 300,
                "mean_seconds_to_resolve": 1800,
            }
        ]
        cls.sample_team_data = [
            {
                "team_id": "TEAM1",
                "team_name": "Eng",
                "total_incident_count": 20,
                "mean_seconds_to_first_ack": 240,
            }
        ]
        cls.sample_load_data = [
            {
                "responder_id": "USER1",
                "responder_name": "Alice",
                "total_seconds_on_call": 86400,
                "total_incident_count": 5,
            }
        ]
        cls.sample_all_data = {
            "total_incident_count": 50,
            "mean_seconds_to_first_ack": 200,
            "mean_seconds_to_resolve": 900,
            "p50_seconds_to_resolve": 600,
            "p90_seconds_to_resolve": 1800,
        }

    # --- get_responder_metrics ---

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_responder_metrics_dict_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": self.sample_responder_data}
        mock_get_client.return_value = mock_client

        request = GetResponderMetricsRequest(filters=self.responder_filters)
        result = get_responder_metrics(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["response"]), 1)
        self.assertEqual(parsed["response"][0]["responder_id"], "USER1")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/responders/teams", json=request.to_body()
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_responder_metrics_list_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = self.sample_responder_data
        mock_get_client.return_value = mock_client

        request = GetResponderMetricsRequest(filters=self.responder_filters)
        result = get_responder_metrics(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["response"]), 1)

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_responder_metrics_empty(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetResponderMetricsRequest(filters=self.responder_filters)
        result = get_responder_metrics(request)

        parsed = json.loads(result)
        self.assertEqual(parsed["response"], [])

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_responder_metrics_with_filters(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": self.sample_responder_data}
        mock_get_client.return_value = mock_client

        filters = AnalyticsFilters(
            date_range_start="2026-01-01T00:00:00Z",
            date_range_end="2026-01-31T23:59:59Z",
            team_ids=["TEAM1"],
            urgency="high",
        )
        request = GetResponderMetricsRequest(
            filters=filters, time_zone="America/New_York", order="desc", order_by="total_interruptions"
        )
        body = request.to_body()

        get_responder_metrics(request)

        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/responders/teams", json=body
        )
        self.assertIn("team_ids", body["filters"])
        self.assertEqual(body["time_zone"], "America/New_York")

    # --- get_incident_metrics_by_service ---

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_incident_metrics_by_service_dict_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": self.sample_service_data}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByServiceRequest(filters=self.incident_filters)
        result = get_incident_metrics_by_service(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["response"]), 1)
        self.assertEqual(parsed["response"][0]["service_id"], "SVC1")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/services", json=request.to_body()
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_incident_metrics_by_service_empty(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByServiceRequest(filters=self.incident_filters)
        result = get_incident_metrics_by_service(request)

        parsed = json.loads(result)
        self.assertEqual(parsed["response"], [])

    # --- get_incident_metrics_by_team ---

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_incident_metrics_by_team_dict_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": self.sample_team_data}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByTeamRequest(filters=self.incident_filters)
        result = get_incident_metrics_by_team(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["response"]), 1)
        self.assertEqual(parsed["response"][0]["team_id"], "TEAM1")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/teams", json=request.to_body()
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_incident_metrics_by_team_with_aggregate_unit(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": self.sample_team_data}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByTeamRequest(
            filters=self.incident_filters, aggregate_unit="week"
        )
        body = request.to_body()

        get_incident_metrics_by_team(request)

        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/teams", json=body
        )
        self.assertEqual(body["aggregate_unit"], "week")

    # --- get_responder_load_metrics ---

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_responder_load_metrics_dict_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": self.sample_load_data}
        mock_get_client.return_value = mock_client

        request = GetResponderLoadMetricsRequest(filters=self.responder_filters)
        result = get_responder_load_metrics(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["response"]), 1)
        self.assertEqual(parsed["response"][0]["responder_id"], "USER1")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/responders/all", json=request.to_body()
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_responder_load_metrics_list_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = self.sample_load_data
        mock_get_client.return_value = mock_client

        request = GetResponderLoadMetricsRequest(filters=self.responder_filters)
        result = get_responder_load_metrics(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["response"]), 1)

    # --- get_incident_metrics_all ---

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_incident_metrics_all_dict_with_data_list(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": [self.sample_all_data]}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsAllRequest(filters=self.incident_filters)
        result = get_incident_metrics_all(request)

        parsed = json.loads(result)
        self.assertEqual(parsed["total_incident_count"], 50)
        self.assertEqual(parsed["p90_seconds_to_resolve"], 1800)
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/all", json=request.to_body()
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_get_incident_metrics_all_empty_data(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsAllRequest(filters=self.incident_filters)
        result = get_incident_metrics_all(request)

        parsed = json.loads(result)
        self.assertIsNone(parsed["total_incident_count"])

    # --- Model tests ---

    def test_analytics_responder_metrics_model(self):
        m = AnalyticsResponderMetrics(
            responder_id="U1",
            responder_name="Alice",
            total_seconds_on_call=3600,
            total_interruptions=3,
        )
        self.assertEqual(m.responder_id, "U1")
        self.assertEqual(m.total_seconds_on_call, 3600)

    def test_analytics_aggregated_metrics_defaults(self):
        m = AnalyticsAggregatedMetrics()
        self.assertIsNone(m.total_incident_count)
        self.assertIsNone(m.p50_seconds_to_resolve)

    def test_get_responder_metrics_request_to_body_minimal(self):
        filters = AnalyticsFilters(
            date_range_start="2026-01-01T00:00:00Z",
            date_range_end="2026-01-31T23:59:59Z",
        )
        req = GetResponderMetricsRequest(filters=filters)
        body = req.to_body()
        self.assertIn("filters", body)
        self.assertEqual(body["filters"]["date_range_start"], "2026-01-01T00:00:00Z")
        self.assertNotIn("time_zone", body)
        self.assertNotIn("team_ids", body["filters"])

    def test_get_responder_metrics_request_to_body_full(self):
        filters = AnalyticsFilters(
            date_range_start="2026-01-01T00:00:00Z",
            date_range_end="2026-01-31T23:59:59Z",
            team_ids=["T1"],
            urgency="high",
        )
        req = GetResponderMetricsRequest(
            filters=filters, time_zone="UTC", order="asc", order_by="total_interruptions"
        )
        body = req.to_body()
        self.assertEqual(body["filters"]["team_ids"], ["T1"])
        self.assertEqual(body["time_zone"], "UTC")
        self.assertEqual(body["order"], "asc")


if __name__ == "__main__":
    unittest.main()
