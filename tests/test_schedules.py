import unittest
from unittest.mock import MagicMock, patch

from pagerduty.errors import HttpError

from pagerduty_mcp.models import Schedule, ScheduleQuery, ScheduleV3, ScheduleV3Create, ScheduleV3Update
from pagerduty_mcp.tools.schedules import (
    create_schedule,
    get_schedule,
    list_schedules,
    update_schedule,
)
from pagerduty_mcp.tools.schedules_v3 import _check_v3_response

SCHED = "pagerduty_mcp.tools.schedules"


def _http_error(status: int, message: str) -> HttpError:
    """Build a pagerduty HttpError whose .response mimics the API error body."""
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {"error": {"message": message}}
    return HttpError(f"HTTP {status}", resp)


def _v2_raw(schedule_id: str, name: str) -> dict:
    return {"id": schedule_id, "name": name, "summary": name, "time_zone": "UTC"}


class TestListSchedulesUnified(unittest.TestCase):
    """The unified list must surface BOTH systems and never hide a partial failure."""

    @patch(f"{SCHED}._get_v3_schedules_page")
    @patch(f"{SCHED}.paginate")
    @patch(f"{SCHED}.get_client")
    def test_merges_v2_and_v3_tagged_by_kind(self, _client, mock_paginate, mock_v3_page):
        mock_paginate.return_value = [_v2_raw("PKSA96L", "Primary")]
        mock_v3_page.return_value = ([{"id": "PK4N098", "name": "Shift A", "time_zone": "UTC"}], False)

        result = list_schedules(ScheduleQuery())

        kinds = {s.id: s.kind for s in result.response}
        self.assertEqual(kinds, {"PKSA96L": "layer_based", "PK4N098": "shift_based"})
        self.assertFalse(result.degraded)
        self.assertEqual({s.api: s.status for s in result.sources}, {"v2": "ok", "v3": "ok"})

    @patch(f"{SCHED}.get_schedule_v3")
    @patch(f"{SCHED}._get_v3_schedules_page")
    @patch(f"{SCHED}.paginate")
    @patch(f"{SCHED}.get_client")
    def test_enriches_v3_null_names(self, _client, mock_paginate, mock_v3_page, mock_get_v3):
        mock_paginate.return_value = []
        mock_v3_page.return_value = ([{"id": "PK4N098", "name": None}], False)
        mock_get_v3.return_value = ScheduleV3(id="PK4N098", name="Enriched", time_zone="UTC")

        result = list_schedules(ScheduleQuery(), enrich=True)

        self.assertEqual(result.response[0].name, "Enriched")
        mock_get_v3.assert_called_once_with("PK4N098")

    @patch(f"{SCHED}.get_schedule_v3")
    @patch(f"{SCHED}._get_v3_schedules_page")
    @patch(f"{SCHED}.paginate")
    @patch(f"{SCHED}.get_client")
    def test_enrich_false_skips_lookups_and_notes_it(self, _client, mock_paginate, mock_v3_page, mock_get_v3):
        mock_paginate.return_value = []
        mock_v3_page.return_value = ([{"id": "PK4N098", "name": None}], False)

        result = list_schedules(ScheduleQuery(), enrich=False)

        self.assertIsNone(result.response[0].name)
        mock_get_v3.assert_not_called()
        v3_source = next(s for s in result.sources if s.api == "v3")
        self.assertIn("not enriched", v3_source.message or "")

    @patch(f"{SCHED}.get_schedule_v3")
    @patch(f"{SCHED}._get_v3_schedules_page")
    @patch(f"{SCHED}.paginate")
    @patch(f"{SCHED}.get_client")
    @patch(f"{SCHED}._V3_ENRICH_CAP", 2)
    def test_enrichment_is_bounded_by_cap(self, _client, mock_paginate, mock_v3_page, mock_get_v3):
        mock_paginate.return_value = []
        mock_v3_page.return_value = (
            [{"id": f"P{i}", "name": None} for i in range(3)],
            False,
        )
        mock_get_v3.side_effect = lambda sid: ScheduleV3(id=sid, name=f"name-{sid}")

        result = list_schedules(ScheduleQuery(), enrich=True)

        self.assertEqual(mock_get_v3.call_count, 2)  # capped at 2, not 3
        v3_source = next(s for s in result.sources if s.api == "v3")
        self.assertIn("1 shift-based", v3_source.message or "")  # 1 left un-enriched

    @patch(f"{SCHED}._get_v3_schedules_page")
    @patch(f"{SCHED}.paginate")
    @patch(f"{SCHED}.get_client")
    def test_v3_failure_keeps_v2_and_marks_incomplete(self, _client, mock_paginate, mock_v3_page):
        mock_paginate.return_value = [_v2_raw("PKSA96L", "Primary")]
        mock_v3_page.side_effect = RuntimeError("v3 down")

        result = list_schedules(ScheduleQuery())

        self.assertTrue(result.degraded)
        self.assertIn("PKSA96L", [s.id for s in result.response])  # v2 retained
        self.assertEqual(next(s for s in result.sources if s.api == "v3").status, "error")
        self.assertIn("INCOMPLETE", result.response_summary)

    @patch(f"{SCHED}._get_v3_schedules_page")
    @patch(f"{SCHED}.paginate")
    @patch(f"{SCHED}.get_client")
    def test_v2_failure_keeps_v3_and_marks_incomplete(self, _client, mock_paginate, mock_v3_page):
        mock_paginate.side_effect = RuntimeError("v2 down")
        mock_v3_page.return_value = ([{"id": "PK4N098", "name": "Shift A"}], False)

        result = list_schedules(ScheduleQuery())

        self.assertTrue(result.degraded)
        self.assertIn("PK4N098", [s.id for s in result.response])  # v3 retained
        self.assertEqual(next(s for s in result.sources if s.api == "v2").status, "error")
        self.assertIn("INCOMPLETE", result.response_summary)


class TestGetScheduleRouting(unittest.TestCase):
    """get_schedule resolves the kind itself; the hint is an optimization, never required."""

    @patch(f"{SCHED}.get_schedule_v3")
    def test_kind_hint_shift_based_goes_straight_to_v3(self, mock_get_v3):
        mock_get_v3.return_value = ScheduleV3(id="PK4N098", name="Shift")
        result = get_schedule("PK4N098", kind="shift_based")
        self.assertIsInstance(result, ScheduleV3)
        mock_get_v3.assert_called_once_with("PK4N098")

    @patch(f"{SCHED}.get_client")
    def test_kind_hint_layer_based_uses_v2(self, mock_get_client):
        client = MagicMock()
        client.rget.return_value = _v2_raw("PKSA96L", "Primary")
        mock_get_client.return_value = client

        result = get_schedule("PKSA96L", kind="layer_based")

        self.assertIsInstance(result, Schedule)
        client.rget.assert_called_once_with("/schedules/PKSA96L")

    @patch(f"{SCHED}.get_client")
    def test_no_hint_v2_success(self, mock_get_client):
        client = MagicMock()
        client.rget.return_value = _v2_raw("PKSA96L", "Primary")
        mock_get_client.return_value = client

        result = get_schedule("PKSA96L")

        self.assertIsInstance(result, Schedule)
        self.assertEqual(result.kind, "layer_based")

    @patch(f"{SCHED}.get_schedule_v3")
    @patch(f"{SCHED}.get_client")
    def test_no_hint_falls_back_to_v3_on_specific_400(self, mock_get_client, mock_get_v3):
        client = MagicMock()
        client.rget.side_effect = _http_error(
            400, "This is a shift-based schedule. Use the v3 Schedules API to access it."
        )
        mock_get_client.return_value = client
        mock_get_v3.return_value = ScheduleV3(id="PK4N098", name="Shift")

        result = get_schedule("PK4N098")

        self.assertIsInstance(result, ScheduleV3)
        mock_get_v3.assert_called_once_with("PK4N098")

    @patch(f"{SCHED}.get_schedule_v3")
    @patch(f"{SCHED}.get_client")
    def test_no_hint_reraises_non_redirect_404(self, mock_get_client, mock_get_v3):
        client = MagicMock()
        client.rget.side_effect = _http_error(404, "Not Found")
        mock_get_client.return_value = client

        with self.assertRaises(HttpError):
            get_schedule("MISSING")
        mock_get_v3.assert_not_called()  # no error-swallowing

    @patch(f"{SCHED}.get_schedule_v3")
    @patch(f"{SCHED}.get_client")
    def test_no_hint_reraises_generic_400(self, mock_get_client, mock_get_v3):
        client = MagicMock()
        client.rget.side_effect = _http_error(400, "Invalid query parameter")
        mock_get_client.return_value = client

        with self.assertRaises(HttpError):
            get_schedule("PXXXX")
        mock_get_v3.assert_not_called()


class TestCreateUpdateRouting(unittest.TestCase):
    """Create/update target shift-based (v3); a v2 id surfaces the API's guidance, never a no-op."""

    @patch(f"{SCHED}.create_schedule_v3")
    def test_create_routes_to_v3(self, mock_create_v3):
        mock_create_v3.return_value = ScheduleV3(id="PK4N098", name="New")
        data = ScheduleV3Create(name="New", time_zone="UTC")

        result = create_schedule(data)

        self.assertIsInstance(result, ScheduleV3)
        mock_create_v3.assert_called_once_with(data)

    @patch(f"{SCHED}.update_schedule_v3")
    def test_update_routes_to_v3(self, mock_update_v3):
        mock_update_v3.return_value = ScheduleV3(id="PK4N098", name="Renamed")
        data = ScheduleV3Update(name="Renamed")

        result = update_schedule("PK4N098", data)

        self.assertIsInstance(result, ScheduleV3)
        mock_update_v3.assert_called_once_with("PK4N098", data)

    @patch(f"{SCHED}.update_schedule_v3")
    def test_update_on_v2_id_surfaces_self_describing_error(self, mock_update_v3):
        mock_update_v3.side_effect = RuntimeError(
            "PagerDuty v3 Schedules API error (HTTP 400): "
            "This is a layer-based schedule. Use the v2 Schedules API to access it."
        )

        with self.assertRaises(RuntimeError) as ctx:
            update_schedule("PKSA96L", ScheduleV3Update(name="x"))
        self.assertIn("layer-based", str(ctx.exception))


class TestCheckV3Response(unittest.TestCase):
    """The v3 error checker must surface the API's own message, not an opaque failure."""

    def test_raises_with_api_message_on_layer_based_400(self):
        resp = MagicMock()
        resp.ok = False
        resp.status_code = 400
        resp.json.return_value = {
            "error": {"message": "This is a layer-based schedule. Use the v2 Schedules API to access it."}
        }
        with self.assertRaises(RuntimeError) as ctx:
            _check_v3_response(resp)
        self.assertIn("HTTP 400", str(ctx.exception))
        self.assertIn("layer-based", str(ctx.exception))

    def test_noop_on_ok_response(self):
        resp = MagicMock()
        resp.ok = True
        self.assertIsNone(_check_v3_response(resp))


if __name__ == "__main__":
    unittest.main()
