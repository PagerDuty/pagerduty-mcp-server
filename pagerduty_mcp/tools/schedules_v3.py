import logging
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.schedules_v3 import ScheduleV3, ScheduleV3Create, ScheduleV3Update

logger = logging.getLogger(__name__)


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

    response = get_client().rget("/v3/schedules", params=params)

    if isinstance(response, dict) and "schedules" in response:
        raw_schedules = response["schedules"]
    elif isinstance(response, list):
        raw_schedules = response
    else:
        logger.warning("Unexpected response format from /v3/schedules: %s", type(response).__name__)
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
    response = get_client().rget(f"/v3/schedules/{schedule_id}")
    return ScheduleV3.model_validate(_unwrap_schedule(response))


def create_schedule_v3(schedule_data: ScheduleV3Create) -> ScheduleV3:
    """Create a new v3 schedule.

    Args:
        schedule_data: Data for the new v3 schedule, including name, time_zone, and rotations

    Returns:
        The created v3 schedule
    """
    response = get_client().rpost(
        "/v3/schedules",
        json={"schedule": schedule_data.model_dump(exclude_none=True)},
    )
    return ScheduleV3.model_validate(_unwrap_schedule(response))


def update_schedule_v3(schedule_id: str, schedule_data: ScheduleV3Update) -> ScheduleV3:
    """Update an existing v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule to update
        schedule_data: Updated schedule data (only provided fields are changed)

    Returns:
        The updated v3 schedule
    """
    response = get_client().rput(
        f"/v3/schedules/{schedule_id}",
        json={"schedule": schedule_data.model_dump(exclude_none=True)},
    )
    return ScheduleV3.model_validate(_unwrap_schedule(response))
