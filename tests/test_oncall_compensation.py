"""
Unit tests for pagerduty_mcp/tools/oncall_compensation.py
Covers:
  - Pure utility functions (_dedup_shifts, _get_tz_parts, _midnight_ms, _days_in_range,
    _compute_outside_hours)
  - OncallCompensationRequest model validation
  - get_oncall_compensation_report integration (mocked PD client + paginate)
"""
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from pydantic import ValidationError

from pagerduty_mcp.tools.oncall_compensation import (
    COMPLIANCE_TEMPLATES,
    OncallCompensationRequest,
    _compute_outside_hours,
    _days_in_range,
    _dedup_shifts,
    _get_tz_parts,
    _midnight_ms,
    get_oncall_compensation_report,
)


# ── Pure function tests ──────────────────────────────────────────────────────

class TestOncallCompensationPureFunctions(unittest.TestCase):

    # _dedup_shifts

    def test_dedup_shifts_empty(self):
        self.assertEqual(_dedup_shifts([]), [])

    def test_dedup_shifts_single(self):
        shift = {"start": 1000, "end": 2000}
        result = _dedup_shifts([shift])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 1000)
        self.assertEqual(result[0]["end"], 2000)

    def test_dedup_shifts_overlapping(self):
        # Overlapping: [100, 300) and [200, 400) -> [100, 400)
        shifts = [{"start": 100, "end": 300}, {"start": 200, "end": 400}]
        result = _dedup_shifts(shifts)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 100)
        self.assertEqual(result[0]["end"], 400)

    def test_dedup_shifts_adjacent(self):
        # Adjacent: end == start, should merge
        shifts = [{"start": 100, "end": 200}, {"start": 200, "end": 300}]
        result = _dedup_shifts(shifts)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 100)
        self.assertEqual(result[0]["end"], 300)

    def test_dedup_shifts_non_overlapping(self):
        shifts = [{"start": 100, "end": 200}, {"start": 300, "end": 400}]
        result = _dedup_shifts(shifts)
        self.assertEqual(len(result), 2)

    def test_dedup_shifts_sorts_by_start(self):
        # Input in reverse order — should still sort and merge correctly
        shifts = [
            {"start": 300, "end": 500},
            {"start": 100, "end": 350},
        ]
        result = _dedup_shifts(shifts)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start"], 100)
        self.assertEqual(result[0]["end"], 500)

    # _get_tz_parts

    def test_get_tz_parts_utc(self):
        # Timestamp 0 is 1970-01-01T00:00:00Z (Thursday)
        parts = _get_tz_parts(0, "UTC")
        self.assertEqual(parts["year"], 1970)
        self.assertEqual(parts["month"], 1)
        self.assertEqual(parts["day"], 1)
        self.assertEqual(parts["hour"], 0)
        self.assertEqual(parts["weekday"], 4)  # Thursday in ISO = 4

    # _midnight_ms

    def test_midnight_ms_utc(self):
        expected = datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp() * 1000
        result = _midnight_ms("2023-01-01", "UTC")
        self.assertAlmostEqual(result, expected, places=0)

    # _days_in_range

    def test_days_in_range_single_day(self):
        # Start and end within same day
        ts_ms = datetime(2023, 1, 2, 9, 0, tzinfo=timezone.utc).timestamp() * 1000
        end_ms = datetime(2023, 1, 2, 17, 0, tzinfo=timezone.utc).timestamp() * 1000
        result = _days_in_range(ts_ms, end_ms, "UTC")
        self.assertEqual(result, ["2023-01-02"])

    def test_days_in_range_multi_day(self):
        # Span 3 days: Jan 2, 3, 4
        start_ms = datetime(2023, 1, 2, 23, 0, tzinfo=timezone.utc).timestamp() * 1000
        end_ms = datetime(2023, 1, 4, 1, 0, tzinfo=timezone.utc).timestamp() * 1000
        result = _days_in_range(start_ms, end_ms, "UTC")
        self.assertIn("2023-01-02", result)
        self.assertIn("2023-01-03", result)
        self.assertIn("2023-01-04", result)
        self.assertEqual(len(result), 3)

    # _compute_outside_hours

    def test_compute_outside_hours_empty_shifts(self):
        result = _compute_outside_hours([], 9, 18, {1, 2, 3, 4, 5}, set(), "UTC")
        self.assertEqual(result["outside_hours"], 0.0)
        self.assertEqual(result["weekend_hours"], 0.0)
        self.assertEqual(result["holiday_hours"], 0.0)
        self.assertEqual(result["weeknight_hours"], 0.0)
        self.assertEqual(result["weekend_period_count"], 0)
        self.assertEqual(result["holiday_count"], 0)
        self.assertEqual(result["unique_ooh_periods"], 0)
        self.assertEqual(result["max_consecutive_on_call_hours"], 0.0)
        self.assertEqual(result["max_consecutive_on_call_days"], 0)
        self.assertEqual(result["min_rest_hours"], 999.0)

    def test_compute_outside_hours_business_hours_only(self):
        # Mon Jan 2 2023 09:00 - 17:00 UTC is entirely within biz hours (9-18, Mon-Fri)
        start_ms = datetime(2023, 1, 2, 9, 0, tzinfo=timezone.utc).timestamp() * 1000
        end_ms = datetime(2023, 1, 2, 17, 0, tzinfo=timezone.utc).timestamp() * 1000
        shifts = [{"start": start_ms, "end": end_ms}]
        result = _compute_outside_hours(shifts, 9, 18, {1, 2, 3, 4, 5}, set(), "UTC")
        self.assertEqual(result["outside_hours"], 0.0)
        self.assertEqual(result["weekend_hours"], 0.0)
        self.assertEqual(result["weeknight_hours"], 0.0)

    def test_compute_outside_hours_weekend(self):
        # Jan 7 2023 is Saturday (weekday ISO = 6)
        start_ms = datetime(2023, 1, 7, 9, 0, tzinfo=timezone.utc).timestamp() * 1000
        end_ms = datetime(2023, 1, 7, 17, 0, tzinfo=timezone.utc).timestamp() * 1000
        shifts = [{"start": start_ms, "end": end_ms}]
        result = _compute_outside_hours(shifts, 9, 18, {1, 2, 3, 4, 5}, set(), "UTC")
        self.assertGreater(result["weekend_hours"], 0)
        self.assertGreater(result["outside_hours"], 0)


# ── Model validation tests ───────────────────────────────────────────────────

class TestOncallCompensationRequest(unittest.TestCase):

    def test_request_minimal_valid(self):
        req = OncallCompensationRequest(
            since="2023-01-01T00:00:00Z",
            until="2023-01-31T23:59:59Z",
        )
        self.assertEqual(req.since, "2023-01-01T00:00:00Z")
        self.assertEqual(req.until, "2023-01-31T23:59:59Z")

    def test_request_extra_fields_forbidden(self):
        with self.assertRaises(ValidationError):
            OncallCompensationRequest(
                since="2023-01-01T00:00:00Z",
                until="2023-01-31T23:59:59Z",
                unknown_field="oops",
            )

    def test_request_compliance_template_default(self):
        req = OncallCompensationRequest(
            since="2023-01-01T00:00:00Z",
            until="2023-01-31T23:59:59Z",
        )
        self.assertEqual(req.compliance_template, "none")

    def test_request_biz_hours_defaults(self):
        req = OncallCompensationRequest(
            since="2023-01-01T00:00:00Z",
            until="2023-01-31T23:59:59Z",
        )
        self.assertEqual(req.biz_start_hour, 9)
        self.assertEqual(req.biz_end_hour, 18)

    def test_request_work_days_default(self):
        req = OncallCompensationRequest(
            since="2023-01-01T00:00:00Z",
            until="2023-01-31T23:59:59Z",
        )
        self.assertEqual(req.work_days, [1, 2, 3, 4, 5])

    def test_compliance_templates_dict(self):
        self.assertIn("emea", COMPLIANCE_TEMPLATES)
        self.assertIn("us", COMPLIANCE_TEMPLATES)
        self.assertIn("none", COMPLIANCE_TEMPLATES)
        self.assertEqual(COMPLIANCE_TEMPLATES["emea"]["hours_cap"], 192)


# ── Integration tests ────────────────────────────────────────────────────────

class TestGetOncallCompensationReport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sample_analytics_data = {
            "data": [{
                "responder_id": "U1",
                "responder_name": "Alice",
                "team_id": "T1",
                "total_seconds_on_call": 72000,       # 20 hours
                "total_seconds_on_call_level_1": 72000,
                "total_seconds_on_call_level_2_plus": 0,
                "total_interruptions": 5,
                "total_business_hour_interruptions": 3,
                "total_off_hour_interruptions": 2,
                "total_sleep_hour_interruptions": 0,
                "total_engaged_seconds": 3600,
                "total_incident_count": 3,
                "mean_time_to_acknowledge_seconds": 120,
            }]
        }

        # Mon Jan 2 2023 09:00 - 17:00 UTC (business hours shift)
        cls.sample_oncalls = [{
            "user": {"id": "U1", "summary": "Alice"},
            "schedule": {"id": "SCHED1"},
            "escalation_policy": {"id": "EP1"},
            "escalation_level": 1,
            "start": "2023-01-02T09:00:00Z",
            "end": "2023-01-02T17:00:00Z",
        }]

        cls.sample_incidents = [{
            "id": "INC1",
            "urgency": "high",
            "assignments": [{"assignee": {"id": "U1"}}],
        }]

        cls.sample_teams = [{"id": "T1", "name": "Engineering"}]
        cls.sample_users = [{"id": "U1", "name": "Alice", "time_zone": "UTC"}]

    # ── helpers ──────────────────────────────────────────────────────────────

    def _make_request(self, **kwargs):
        defaults = {
            "since": "2023-01-01T00:00:00Z",
            "until": "2023-01-31T23:59:59Z",
        }
        defaults.update(kwargs)
        return OncallCompensationRequest(**defaults)

    # ── tests ────────────────────────────────────────────────────────────────

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_basic(self, mock_get_client, mock_paginate):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.rpost.return_value = self.sample_analytics_data
        mock_paginate.side_effect = [
            self.sample_oncalls,    # oncalls
            self.sample_incidents,  # incidents
            self.sample_teams,      # teams
            self.sample_users,      # users
        ]

        request = self._make_request()
        result = get_oncall_compensation_report(request)

        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertEqual(parsed["total_users"], 1)
        self.assertEqual(parsed["users"][0]["user_id"], "U1")
        self.assertEqual(parsed["users"][0]["scheduled_hours"], 20.0)
        self.assertEqual(parsed["since"], "2023-01-01T00:00:00Z")
        self.assertEqual(parsed["until"], "2023-01-31T23:59:59Z")

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_forward_mode(self, mock_get_client, mock_paginate):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        # paginate called 3 times in forward mode (no incidents)
        mock_paginate.side_effect = [
            self.sample_oncalls,   # oncalls
            self.sample_teams,     # teams
            self.sample_users,     # users
        ]

        request = self._make_request(forward=True)
        result = get_oncall_compensation_report(request)

        parsed = json.loads(result)
        self.assertTrue(parsed["is_forward"])
        user_ids = [u["user_id"] for u in parsed["users"]]
        self.assertIn("U1", user_ids)
        # rpost (analytics) must NOT be called in forward mode
        mock_client.rpost.assert_not_called()

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_empty_no_users(self, mock_get_client, mock_paginate):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.rpost.return_value = {"data": []}
        mock_paginate.side_effect = [
            [],  # oncalls
            [],  # incidents
            [],  # teams
            [],  # users
        ]

        request = self._make_request()
        result = get_oncall_compensation_report(request)

        parsed = json.loads(result)
        self.assertEqual(parsed["total_users"], 0)
        self.assertEqual(parsed["users"], [])

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_compliance_emea(self, mock_get_client, mock_paginate):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.rpost.return_value = self.sample_analytics_data  # 20h — well under 192h cap
        mock_paginate.side_effect = [
            self.sample_oncalls,
            self.sample_incidents,
            self.sample_teams,
            self.sample_users,
        ]

        request = self._make_request(compliance_template="emea")
        result = get_oncall_compensation_report(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["users"]), 1)
        self.assertEqual(parsed["users"][0]["compliance_status"], "ok")

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_pay_estimation(self, mock_get_client, mock_paginate):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.rpost.return_value = self.sample_analytics_data  # 20h scheduled
        mock_paginate.side_effect = [
            self.sample_oncalls,    # Mon 09:00-17:00 UTC — 8h inside biz hours
            self.sample_incidents,
            self.sample_teams,
            self.sample_users,
        ]

        request = self._make_request(l1_rate_per_hour=10.0)
        result = get_oncall_compensation_report(request)

        parsed = json.loads(result)
        self.assertEqual(len(parsed["users"]), 1)
        # 20h scheduled, 8h inside biz hours, pay must be > 0
        self.assertGreater(parsed["users"][0]["estimated_pay"], 0)

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_team_summary(self, mock_get_client, mock_paginate):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.rpost.return_value = self.sample_analytics_data
        mock_paginate.side_effect = [
            self.sample_oncalls,
            self.sample_incidents,
            self.sample_teams,
            self.sample_users,
        ]

        request = self._make_request()
        result = get_oncall_compensation_report(request)

        parsed = json.loads(result)
        self.assertIn("team_summary", parsed)
        self.assertIsInstance(parsed["team_summary"], list)
        team_names = [t["team_name"] for t in parsed["team_summary"]]
        self.assertIn("Engineering", team_names)

    @patch("pagerduty_mcp.tools.oncall_compensation.paginate")
    @patch("pagerduty_mcp.tools.oncall_compensation.get_client")
    def test_get_oncall_compensation_report_direct_ep_entry(self, mock_get_client, mock_paginate):
        # Direct EP layer: no schedule, no start, no end — counts toward direct_ep_count,
        # but should NOT add shift hours.
        direct_ep_oncall = [{
            "user": {"id": "U1", "summary": "Alice"},
            "schedule": None,
            "escalation_policy": {"id": "EP1"},
            "escalation_level": 1,
            "start": None,
            "end": None,
        }]
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        # Analytics data with 0 scheduled hours
        mock_client.rpost.return_value = {
            "data": [{
                "responder_id": "U1",
                "responder_name": "Alice",
                "team_id": "T1",
                "total_seconds_on_call": 0,
                "total_seconds_on_call_level_1": 0,
                "total_seconds_on_call_level_2_plus": 0,
                "total_interruptions": 0,
                "total_business_hour_interruptions": 0,
                "total_off_hour_interruptions": 0,
                "total_sleep_hour_interruptions": 0,
                "total_engaged_seconds": 0,
                "total_incident_count": 0,
                "mean_time_to_acknowledge_seconds": 0,
            }]
        }
        mock_paginate.side_effect = [
            direct_ep_oncall,       # oncalls
            [],                     # incidents
            self.sample_teams,      # teams
            self.sample_users,      # users
        ]

        request = self._make_request()
        result = get_oncall_compensation_report(request)

        parsed = json.loads(result)
        # User should be present (from analytics) with direct_ep_count >= 1
        user = next((u for u in parsed["users"] if u["user_id"] == "U1"), None)
        self.assertIsNotNone(user)
        self.assertGreaterEqual(user["direct_ep_count"], 1)
        # Scheduled hours should remain 0 — no shift window was added
        self.assertEqual(user["scheduled_hours"], 0.0)


if __name__ == "__main__":
    unittest.main()
