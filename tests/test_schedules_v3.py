import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.escalation_policies import EscalationTarget
from pagerduty_mcp.models.schedules_v3 import (
    CustomShift,
    CustomShiftCreate,
    CustomShiftUpdate,
    OverrideShift,
    OverrideShiftCreate,
    Rotation,
    RotationEvent,
    RotationEventCreate,
    RotationEventUpdate,
    ScheduleV3,
    ScheduleV3Create,
    ScheduleV3Update,
)
from pagerduty_mcp.tools.schedules_v3 import (
    create_schedule_v3,
    create_schedule_v3_custom_shifts,
    create_schedule_v3_overrides,
    create_schedule_v3_rotation,
    create_schedule_v3_rotation_event,
    delete_schedule_v3_custom_shift,
    delete_schedule_v3_override,
    delete_schedule_v3_rotation,
    delete_schedule_v3_rotation_event,
    get_schedule_v3,
    get_schedule_v3_custom_shift,
    get_schedule_v3_override,
    get_schedule_v3_rotation,
    get_schedule_v3_rotation_event,
    list_schedule_v3_custom_shifts,
    list_schedule_v3_overrides,
    list_schedule_v3_rotation_events,
    list_schedule_v3_rotations,
    list_schedules_v3,
    update_schedule_v3,
    update_schedule_v3_custom_shift,
    update_schedule_v3_override,
    update_schedule_v3_rotation_event,
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


class TestScheduleV3RotationTools(unittest.TestCase):
    """Test v3 schedule rotation tool functions."""

    @classmethod
    def setUpClass(cls):
        cls.schedule_id = "SCHED123"
        cls.rotation_id = "ROT123"
        cls.sample_rotation = {"id": "ROT123", "type": "rotation"}
        cls.mock_client = MagicMock()
        cls.mock_client.url = BASE_URL

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.url = BASE_URL
        self.mock_client.get.side_effect = None
        self.mock_client.post.side_effect = None
        self.mock_client.delete.side_effect = None

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedule_v3_rotations(self, mock_get_client):
        """Test list_schedule_v3_rotations returns a list of Rotation objects."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"rotations": [self.sample_rotation]})

        result = list_schedule_v3_rotations(self.schedule_id)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations"
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], Rotation)
        self.assertEqual(result.response[0].id, "ROT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_create_schedule_v3_rotation(self, mock_get_client):
        """Test create_schedule_v3_rotation posts correct payload and returns Rotation."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.post.return_value = _mock_response({"rotation": self.sample_rotation})

        result = create_schedule_v3_rotation(self.schedule_id)

        self.mock_client.post.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations",
            json={},
        )
        self.assertIsInstance(result, Rotation)
        self.assertEqual(result.id, "ROT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_get_schedule_v3_rotation(self, mock_get_client):
        """Test get_schedule_v3_rotation fetches a single rotation by id."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"rotation": self.sample_rotation})

        result = get_schedule_v3_rotation(self.schedule_id, self.rotation_id)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}"
        )
        self.assertIsInstance(result, Rotation)
        self.assertEqual(result.id, "ROT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_delete_schedule_v3_rotation(self, mock_get_client):
        """Test delete_schedule_v3_rotation sends DELETE and returns confirmation string."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.delete.return_value = _mock_response({})

        result = delete_schedule_v3_rotation(self.schedule_id, self.rotation_id)

        self.mock_client.delete.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}"
        )
        self.assertIsInstance(result, str)
        self.assertIn(self.rotation_id, result)
        self.assertIn(self.schedule_id, result)


class TestScheduleV3RotationEventTools(unittest.TestCase):
    """Test v3 schedule rotation event tool functions."""

    @classmethod
    def setUpClass(cls):
        cls.schedule_id = "SCHED123"
        cls.rotation_id = "ROT123"
        cls.event_id = "EVT123"
        cls.sample_event = {
            "id": "EVT123",
            "name": "Weekly On-Call",
            "recurrence": ["RRULE:FREQ=WEEKLY"],
        }
        cls.mock_client = MagicMock()
        cls.mock_client.url = BASE_URL

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.url = BASE_URL
        self.mock_client.get.side_effect = None
        self.mock_client.post.side_effect = None
        self.mock_client.put.side_effect = None
        self.mock_client.delete.side_effect = None

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedule_v3_rotation_events(self, mock_get_client):
        """Test list_schedule_v3_rotation_events returns a list of RotationEvent objects."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"events": [self.sample_event]})

        result = list_schedule_v3_rotation_events(self.schedule_id, self.rotation_id)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}/events"
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], RotationEvent)
        self.assertEqual(result.response[0].id, "EVT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_create_schedule_v3_rotation_event(self, mock_get_client):
        """Test create_schedule_v3_rotation_event posts correct payload and returns RotationEvent."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.post.return_value = _mock_response({"event": self.sample_event})

        event_data = RotationEventCreate(
            name="Weekly On-Call",
            start_time={"date_time": "2025-03-15T09:00:00Z", "time_zone": "UTC"},
            end_time={"date_time": "2025-03-15T17:00:00Z", "time_zone": "UTC"},
            effective_since="2025-03-15T09:00:00Z",
            recurrence=["RRULE:FREQ=WEEKLY"],
            assignment_strategy={
                "type": "rotating_member_assignment_strategy",
                "members": [{"type": "user_member", "user_id": "USER123"}],
                "shifts_per_member": 1,
            },
        )
        result = create_schedule_v3_rotation_event(self.schedule_id, self.rotation_id, event_data)

        self.mock_client.post.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}/events",
            json={"event": event_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, RotationEvent)
        self.assertEqual(result.id, "EVT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_get_schedule_v3_rotation_event(self, mock_get_client):
        """Test get_schedule_v3_rotation_event fetches a single rotation event by id."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"event": self.sample_event})

        result = get_schedule_v3_rotation_event(self.schedule_id, self.rotation_id, self.event_id)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}/events/{self.event_id}"
        )
        self.assertIsInstance(result, RotationEvent)
        self.assertEqual(result.id, "EVT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_update_schedule_v3_rotation_event(self, mock_get_client):
        """Test update_schedule_v3_rotation_event puts correct payload and returns RotationEvent."""
        mock_get_client.return_value = self.mock_client
        updated = dict(self.sample_event)
        updated["name"] = "Monthly On-Call"
        self.mock_client.put.return_value = _mock_response({"event": updated})

        event_data = RotationEventUpdate(
            name="Monthly On-Call",
            start_time={"date_time": "2025-03-15T09:00:00Z", "time_zone": "UTC"},
            end_time={"date_time": "2025-03-15T17:00:00Z", "time_zone": "UTC"},
            effective_since="2025-03-15T09:00:00Z",
            recurrence=["RRULE:FREQ=MONTHLY"],
            assignment_strategy={
                "type": "rotating_member_assignment_strategy",
                "members": [{"type": "user_member", "user_id": "USER123"}],
                "shifts_per_member": 1,
            },
        )
        result = update_schedule_v3_rotation_event(
            self.schedule_id, self.rotation_id, self.event_id, event_data
        )

        self.mock_client.put.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}/events/{self.event_id}",
            json={"event": event_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, RotationEvent)
        self.assertEqual(result.name, "Monthly On-Call")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_delete_schedule_v3_rotation_event(self, mock_get_client):
        """Test delete_schedule_v3_rotation_event sends DELETE and returns confirmation string."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.delete.return_value = _mock_response({})

        result = delete_schedule_v3_rotation_event(
            self.schedule_id, self.rotation_id, self.event_id
        )

        self.mock_client.delete.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/rotations/{self.rotation_id}/events/{self.event_id}"
        )
        self.assertIsInstance(result, str)
        self.assertIn(self.event_id, result)
        self.assertIn(self.rotation_id, result)


class TestScheduleV3CustomShiftTools(unittest.TestCase):
    """Test v3 schedule custom shift tool functions."""

    @classmethod
    def setUpClass(cls):
        cls.schedule_id = "SCHED123"
        cls.custom_shift_id = "CSHIFT123"
        cls.since = "2025-03-15T00:00:00Z"
        cls.until = "2025-03-22T00:00:00Z"
        cls.sample_shift = {
            "id": "CSHIFT123",
            "type": "custom_shift",
            "start_time": "2025-03-15T09:00:00Z",
            "end_time": "2025-03-15T17:00:00Z",
        }
        cls.mock_client = MagicMock()
        cls.mock_client.url = BASE_URL

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.url = BASE_URL
        self.mock_client.get.side_effect = None
        self.mock_client.post.side_effect = None
        self.mock_client.put.side_effect = None
        self.mock_client.delete.side_effect = None

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedule_v3_custom_shifts(self, mock_get_client):
        """Test list_schedule_v3_custom_shifts returns a list of CustomShift objects."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response(
            {"custom_shifts": [self.sample_shift]}
        )

        result = list_schedule_v3_custom_shifts(self.schedule_id, self.since, self.until)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/custom_shifts",
            params={"since": self.since, "until": self.until},
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], CustomShift)
        self.assertEqual(result.response[0].id, "CSHIFT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_create_schedule_v3_custom_shifts(self, mock_get_client):
        """Test create_schedule_v3_custom_shifts posts correct payload and returns list."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.post.return_value = _mock_response(
            {"custom_shifts": [self.sample_shift]}
        )

        shift_create = CustomShiftCreate(
            start_time="2025-03-15T09:00:00Z",
            end_time="2025-03-15T17:00:00Z",
            assignments=[
                {"type": "shift_assignment", "member": {"type": "user_member", "user_id": "USER123"}}
            ],
        )
        result = create_schedule_v3_custom_shifts(self.schedule_id, [shift_create])

        self.mock_client.post.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/custom_shifts",
            json={"custom_shifts": [shift_create.model_dump(exclude_none=True)]},
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], CustomShift)

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_get_schedule_v3_custom_shift(self, mock_get_client):
        """Test get_schedule_v3_custom_shift fetches a single custom shift by id."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"custom_shift": self.sample_shift})

        result = get_schedule_v3_custom_shift(self.schedule_id, self.custom_shift_id)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/custom_shifts/{self.custom_shift_id}"
        )
        self.assertIsInstance(result, CustomShift)
        self.assertEqual(result.id, "CSHIFT123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_update_schedule_v3_custom_shift(self, mock_get_client):
        """Test update_schedule_v3_custom_shift puts correct payload and returns CustomShift."""
        mock_get_client.return_value = self.mock_client
        updated = dict(self.sample_shift)
        updated["end_time"] = "2025-03-15T18:00:00Z"
        self.mock_client.put.return_value = _mock_response({"custom_shift": updated})

        shift_data = CustomShiftUpdate(
            start_time="2025-03-15T09:00:00Z",
            end_time="2025-03-15T18:00:00Z",
            assignments=[
                {"type": "shift_assignment", "member": {"type": "user_member", "user_id": "USER123"}}
            ],
        )
        result = update_schedule_v3_custom_shift(
            self.schedule_id, self.custom_shift_id, shift_data
        )

        self.mock_client.put.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/custom_shifts/{self.custom_shift_id}",
            json={"custom_shift": shift_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, CustomShift)
        self.assertEqual(result.end_time, "2025-03-15T18:00:00Z")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_delete_schedule_v3_custom_shift(self, mock_get_client):
        """Test delete_schedule_v3_custom_shift sends DELETE and returns confirmation string."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.delete.return_value = _mock_response({})

        result = delete_schedule_v3_custom_shift(self.schedule_id, self.custom_shift_id)

        self.mock_client.delete.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/custom_shifts/{self.custom_shift_id}"
        )
        self.assertIsInstance(result, str)
        self.assertIn(self.custom_shift_id, result)
        self.assertIn(self.schedule_id, result)


class TestScheduleV3OverrideTools(unittest.TestCase):
    """Test v3 schedule override tool functions."""

    @classmethod
    def setUpClass(cls):
        cls.schedule_id = "SCHED123"
        cls.override_id = "OVRD123"
        cls.since = "2025-03-15T00:00:00Z"
        cls.until = "2025-03-22T00:00:00Z"
        cls.sample_override = {
            "id": "OVRD123",
            "type": "override_shift",
            "start_time": "2025-03-15T09:00:00Z",
            "end_time": "2025-03-15T17:00:00Z",
        }
        cls.mock_client = MagicMock()
        cls.mock_client.url = BASE_URL

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.url = BASE_URL
        self.mock_client.get.side_effect = None
        self.mock_client.post.side_effect = None
        self.mock_client.put.side_effect = None
        self.mock_client.delete.side_effect = None

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_list_schedule_v3_overrides(self, mock_get_client):
        """Test list_schedule_v3_overrides returns a list of OverrideShift objects."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"overrides": [self.sample_override]})

        result = list_schedule_v3_overrides(self.schedule_id, self.since, self.until)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/overrides",
            params={"since": self.since, "until": self.until},
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], OverrideShift)
        self.assertEqual(result.response[0].id, "OVRD123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_create_schedule_v3_overrides(self, mock_get_client):
        """Test create_schedule_v3_overrides posts correct payload and returns list."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.post.return_value = _mock_response({"overrides": [self.sample_override]})

        override_create = OverrideShiftCreate(
            start_time="2025-03-15T09:00:00Z",
            end_time="2025-03-15T17:00:00Z",
            overridden_member={"type": "user_member", "user_id": "USER123"},
            overriding_member={"type": "user_member", "user_id": "USER456"},
        )
        result = create_schedule_v3_overrides(self.schedule_id, [override_create])

        self.mock_client.post.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/overrides",
            json={"overrides": [override_create.model_dump(exclude_none=True)]},
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], OverrideShift)

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_get_schedule_v3_override(self, mock_get_client):
        """Test get_schedule_v3_override fetches a single override by id."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.return_value = _mock_response({"override": self.sample_override})

        result = get_schedule_v3_override(self.schedule_id, self.override_id)

        self.mock_client.get.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/overrides/{self.override_id}"
        )
        self.assertIsInstance(result, OverrideShift)
        self.assertEqual(result.id, "OVRD123")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_update_schedule_v3_override(self, mock_get_client):
        """Test update_schedule_v3_override puts correct payload and returns OverrideShift."""
        mock_get_client.return_value = self.mock_client
        updated = dict(self.sample_override)
        updated["end_time"] = "2025-03-15T18:00:00Z"
        self.mock_client.put.return_value = _mock_response({"override": updated})

        result = update_schedule_v3_override(
            self.schedule_id,
            self.override_id,
            start_time="2025-03-15T09:00:00Z",
            end_time="2025-03-15T18:00:00Z",
            overridden_member_type="user_member",
            overridden_member_user_id="USER123",
            overriding_member_type="user_member",
            overriding_member_user_id="USER456",
        )

        expected_payload = {
            "override": {
                "type": "override_shift",
                "start_time": "2025-03-15T09:00:00Z",
                "end_time": "2025-03-15T18:00:00Z",
                "overridden_member": {"type": "user_member", "user_id": "USER123"},
                "overriding_member": {"type": "user_member", "user_id": "USER456"},
            }
        }
        self.mock_client.put.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/overrides/{self.override_id}",
            json=expected_payload,
        )
        self.assertIsInstance(result, OverrideShift)
        self.assertEqual(result.end_time, "2025-03-15T18:00:00Z")

    @patch("pagerduty_mcp.tools.schedules_v3.get_client")
    def test_delete_schedule_v3_override(self, mock_get_client):
        """Test delete_schedule_v3_override sends DELETE and returns confirmation string."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.delete.return_value = _mock_response({})

        result = delete_schedule_v3_override(self.schedule_id, self.override_id)

        self.mock_client.delete.assert_called_once_with(
            f"{BASE_URL}/v3/schedules/{self.schedule_id}/overrides/{self.override_id}"
        )
        self.assertIsInstance(result, str)
        self.assertIn(self.override_id, result)
        self.assertIn(self.schedule_id, result)
