import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.escalation_policies import EscalationTarget
from pagerduty_mcp.models.schedules_v3 import ScheduleV3, ScheduleV3Create, ScheduleV3Update
from pagerduty_mcp.tools.schedules_v3 import (
    create_schedule_v3,
    get_schedule_v3,
    list_schedules_v3,
    update_schedule_v3,
)

BASE_URL = "https://api.pagerduty.com"


def _mock_response(data):
    """Build a mock requests.Response whose .json() returns data."""
    resp = MagicMock()
    resp.json.return_value = data
    resp.raise_for_status.return_value = None
    return resp


class TestScheduleV3Models(unittest.TestCase):
    """Test v3 schedule model validation."""

    def test_schedule_v3_model_validation(self):
        """Test ScheduleV3 can be constructed from API response data."""
        data = {
            "id": "SCHED123",
            "name": "Engineering On-Call",
            "description": "Primary on-call rotation",
            "time_zone": "America/New_York",
            "type": "schedule",
            "summary": "Engineering On-Call",
        }
        schedule = ScheduleV3(**data)
        self.assertEqual(schedule.id, "SCHED123")
        self.assertEqual(schedule.name, "Engineering On-Call")
        self.assertEqual(schedule.time_zone, "America/New_York")

    def test_schedule_v3_model_optional_fields(self):
        """Test ScheduleV3 works with minimal required fields."""
        schedule = ScheduleV3()
        self.assertIsNone(schedule.id)
        self.assertIsNone(schedule.name)
        self.assertIsNone(schedule.rotations)

    def test_schedule_v3_create_model(self):
        """Test ScheduleV3Create model serialization."""
        create = ScheduleV3Create(
            name="New Schedule",
            time_zone="UTC",
            description="A test schedule",
        )
        dumped = create.model_dump(exclude_none=True)
        self.assertEqual(dumped["name"], "New Schedule")
        self.assertEqual(dumped["time_zone"], "UTC")
        self.assertNotIn("rotations", dumped)

    def test_schedule_v3_update_model_partial(self):
        """Test ScheduleV3Update with only some fields set."""
        update = ScheduleV3Update(name="Updated Name")
        dumped = update.model_dump(exclude_none=True)
        self.assertEqual(dumped["name"], "Updated Name")
        self.assertNotIn("time_zone", dumped)
        self.assertNotIn("rotations", dumped)


class TestEscalationPolicyScheduleV3Reference(unittest.TestCase):
    """Regression test: schedule_v3_reference type must be accepted in EscalationTarget."""

    def test_escalation_target_accepts_schedule_v3_reference(self):
        """EscalationTarget should accept schedule_v3_reference without raising ValidationError.

        This is the core bug fixed by FDE-359: get_escalation_policy was raising
        'Input should be user_reference or schedule_reference' when a v3 schedule was
        referenced in an escalation policy rule.
        """
        target = EscalationTarget(
            id="SCHED_V3_123",
            type="schedule_v3_reference",
            summary="Engineering v3 Schedule",
        )
        self.assertEqual(target.type, "schedule_v3_reference")
        self.assertEqual(target.id, "SCHED_V3_123")

    def test_escalation_target_still_accepts_user_reference(self):
        """EscalationTarget should still accept user_reference (regression guard)."""
        target = EscalationTarget(id="USER123", type="user_reference")
        self.assertEqual(target.type, "user_reference")

    def test_escalation_target_still_accepts_schedule_reference(self):
        """EscalationTarget should still accept schedule_reference (regression guard)."""
        target = EscalationTarget(id="SCHED123", type="schedule_reference")
        self.assertEqual(target.type, "schedule_reference")


class TestScheduleV3Tools(unittest.TestCase):
    """Test v3 schedule tool functions.

    The implementation uses client.get/post/put (requests.Session methods) instead
    of client.rget/rpost/rput, because the pagerduty SDK's r* methods validate paths
    against a hardcoded CANONICAL_PATHS allowlist that doesn't include /v3/schedules.
    Tests therefore mock client.get/post/put and expect .json() to be called on the
    returned response object.
    """

    @classmethod
    def setUpClass(cls):
        cls.sample_schedule = {
            "id": "SCHED123",
            "name": "Engineering On-Call",
            "description": "Primary rotation",
            "time_zone": "America/New_York",
            "type": "schedule",
            "summary": "Engineering On-Call",
        }
        cls.mock_client = MagicMock()
        cls.mock_client.url = BASE_URL

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.url = BASE_URL
        self.mock_client.get.side_effect = None
        self.mock_client.post.side_effect = None
        self.mock_client.put.side_effect = None

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedules_v3_wrapped_response(self, mock_get_client):
        """Test list_schedules_v3 with wrapped API response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"schedules": [self.sample_schedule]})

        result = list_schedules_v3()

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules", params={}
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], ScheduleV3)
        self.assertEqual(result.response[0].id, "SCHED123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedules_v3_list_response(self, mock_get_client):
        """Test list_schedules_v3 with direct list response (SDK unwrapped)."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response([self.sample_schedule])

        result = list_schedules_v3()

        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Engineering On-Call")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedules_v3_with_query(self, mock_get_client):
        """Test list_schedules_v3 passes query param correctly."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"schedules": [self.sample_schedule]})

        list_schedules_v3(query="Engineering", limit=10)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules", params={"query": "Engineering", "limit": 10}
        )

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedules_v3_empty_response(self, mock_get_client):
        """Test list_schedules_v3 with empty result."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"schedules": []})

        result = list_schedules_v3()

        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_get_schedule_v3_wrapped(self, mock_get_client):
        """Test get_schedule_v3 with wrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"schedule": self.sample_schedule})

        result = get_schedule_v3("SCHED123")

        self.mock_client.get.assert_called_once_with(f"{BASE_URL}/v3/schedules/SCHED123")
        self.assertIsInstance(result, ScheduleV3)
        self.assertEqual(result.id, "SCHED123")
        self.assertEqual(result.name, "Engineering On-Call")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_get_schedule_v3_unwrapped(self, mock_get_client):
        """Test get_schedule_v3 with SDK-unwrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response(self.sample_schedule)

        result = get_schedule_v3("SCHED123")

        self.assertIsInstance(result, ScheduleV3)
        self.assertEqual(result.id, "SCHED123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_create_schedule_v3(self, mock_get_client):
        """Test create_schedule_v3 posts correct payload and returns ScheduleV3."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.post.return_value = _mock_response({"schedule": self.sample_schedule})

        schedule_data = ScheduleV3Create(
            name="Engineering On-Call",
            time_zone="America/New_York",
            description="Primary rotation",
        )

        result = create_schedule_v3(schedule_data)

        self.mock_client.post.assert_called_once_with(
            f"{BASE_URL}/v3/schedules",
            json={"schedule": schedule_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, ScheduleV3)
        self.assertEqual(result.id, "SCHED123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_update_schedule_v3(self, mock_get_client):
        """Test update_schedule_v3 puts correct payload and returns ScheduleV3."""
        mock_get_client.return_value = self.mock_client
        updated = dict(self.sample_schedule)
        updated["name"] = "Engineering On-Call (Updated)"
        self.mock_client.put.return_value = _mock_response({"schedule": updated})

        update_data = ScheduleV3Update(name="Engineering On-Call (Updated)")

        result = update_schedule_v3("SCHED123", update_data)

        self.mock_client.put.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/SCHED123",
            json={"schedule": update_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, ScheduleV3)
        self.assertEqual(result.name, "Engineering On-Call (Updated)")


if __name__ == "__main__":
    unittest.main()
