import logging
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.schedules_v3 import ScheduleV3, ScheduleV3Create, ScheduleV3Update

logger = logging.getLogger(__name__)

# The pagerduty SDK's rget/rpost/rput/rdelete validate paths against a hardcoded
# CANONICAL_PATHS allowlist. /v3/schedules is a newer API path not included in
# that list. We use client.get/post/put directly (which goes through the underlying
# requests.Session with auth headers) and construct the full URL ourselves.


def _v3_url(client: Any, path: str) -> str:
    """Build a full v3 API URL from a relative path."""
    return f"{client.url}{path}"


def _unwrap_schedule(response: Any) -> dict:
    """Extract schedule dict from API response, handling both wrapped and unwrapped forms."""
    if isinstance(response, dict) and "schedule" in response:
        return response["schedule"]
    return response


def _extract_api_message(resp: Any) -> str:
    """Pull the human-readable error message out of a v3 API error body."""
    try:
        body = resp.json()
    except Exception:  # noqa: BLE001 - any parse failure falls back to raw text
        return getattr(resp, "text", "") or "unknown error"
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            return err.get("message") or err.get("code") or str(err)
        if isinstance(err, str):
            return err
    return str(body)


def _check_v3_response(resp: Any) -> None:
    """Raise an informative error on a non-2xx v3 response.

    We surface the API's own message (e.g. "This is a layer-based schedule. Use the v2
    Schedules API to access it.") so the caller never gets an opaque failure or a silent no-op.
    """
    if getattr(resp, "ok", True):
        return
    status = getattr(resp, "status_code", "?")
    raise RuntimeError(f"PagerDuty v3 Schedules API error (HTTP {status}): {_extract_api_message(resp)}")


def _get_v3_schedules_page(
    query: str | None = None,
    limit: int | None = None,
) -> tuple[list[dict], bool]:
    """Fetch one page of raw v3 schedule references and whether more pages exist."""
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    if limit:
        params["limit"] = limit

    client = get_client()
    resp = client.get(_v3_url(client, "/v3/schedules"), params=params)
    _check_v3_response(resp)
    data = resp.json()

    if isinstance(data, dict) and "schedules" in data:
        return data["schedules"], bool(data.get("more"))
    if isinstance(data, list):
        return data, False
    logger.warning("Unexpected response format from /v3/schedules: %s", type(data).__name__)
    return [], False


def list_schedules_v3(
    query: str | None = None,
    limit: int | None = None,
) -> ListResponseModel[ScheduleV3]:
    """List v3 (shift-based) schedules. Internal helper — not registered as an MCP tool.

    The unified `list_schedules` tool calls this so the LLM sees a single schedule list.

    Args:
        query: Filter v3 schedules by name
        limit: Max results to return

    Returns:
        List of v3 schedules
    """
    raw_schedules, _ = _get_v3_schedules_page(query=query, limit=limit)
    schedules = [ScheduleV3(**s) for s in raw_schedules]
    return ListResponseModel[ScheduleV3](response=schedules)


def get_schedule_v3(schedule_id: str) -> ScheduleV3:
    """Get a specific v3 schedule by ID.

    Args:
        schedule_id: The ID of the v3 schedule to retrieve

    Returns:
        v3 schedule details including rotations, events, and time zone
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}"))
    _check_v3_response(resp)
    return ScheduleV3.model_validate(_unwrap_schedule(resp.json()))


def create_schedule_v3(schedule_data: ScheduleV3Create) -> ScheduleV3:
    """Create a new v3 schedule.

    Args:
        schedule_data: Data for the new v3 schedule, including name, time_zone, and rotations

    Returns:
        The created v3 schedule
    """
    client = get_client()
    resp = client.post(
        _v3_url(client, "/v3/schedules"),
        json={"schedule": schedule_data.model_dump(exclude_none=True)},
    )
    _check_v3_response(resp)
    return ScheduleV3.model_validate(_unwrap_schedule(resp.json()))


def update_schedule_v3(schedule_id: str, schedule_data: ScheduleV3Update) -> ScheduleV3:
    """Update an existing v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule to update
        schedule_data: Updated schedule data (only provided fields are changed)

    Returns:
        The updated v3 schedule
    """
    client = get_client()
    resp = client.put(
        _v3_url(client, f"/v3/schedules/{schedule_id}"),
        json={"schedule": schedule_data.model_dump(exclude_none=True)},
    )
    _check_v3_response(resp)
    return ScheduleV3.model_validate(_unwrap_schedule(resp.json()))
