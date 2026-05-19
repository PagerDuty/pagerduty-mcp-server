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


def list_schedules_v3(
    query: str | None = None,
    limit: int | None = None,
) -> ListResponseModel[ScheduleV3]:
    """List v3 schedules with optional filtering.

    Use this tool to list schedules created with PagerDuty's next-gen scheduling system (v3).
    Classic (v2) schedules are listed with list_schedules.

    Args:
        query: Filter v3 schedules by name
        limit: Max results to return

    Returns:
        List of v3 schedules
    """
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    if limit:
        params["limit"] = limit

    client = get_client()
    resp = client.get(_v3_url(client, "/v3/schedules"), params=params)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, dict) and "schedules" in data:
        raw_schedules = data["schedules"]
    elif isinstance(data, list):
        raw_schedules = data
    else:
        logger.warning("Unexpected response format from /v3/schedules: %s", type(data).__name__)
        raw_schedules = []

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
    resp.raise_for_status()
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
    resp.raise_for_status()
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
    resp.raise_for_status()
    return ScheduleV3.model_validate(_unwrap_schedule(resp.json()))
