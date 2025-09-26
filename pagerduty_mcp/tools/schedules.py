from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Schedule,
    ScheduleOverrideCreate,
    ScheduleQuery,
    User,
)
from pagerduty_mcp.utils import paginate


def list_schedules(query_model: ScheduleQuery) -> ListResponseModel[Schedule]:
    """List schedules with optional filtering.

    Returns:
        List of schedules matching the query parameters
    """
    response = paginate(client=get_client(), entity="schedules", params=query_model.to_params())
    schedules = [Schedule(**schedule) for schedule in response]
    return ListResponseModel[Schedule](response=schedules)


def get_schedule(schedule_id: str) -> Schedule:
    """Get a specific schedule by ID.

    Args:
        schedule_id: The ID of the schedule to retrieve

    Returns:
        Schedule details
    """
    response = get_client().rget(f"/schedules/{schedule_id}")
    return Schedule.model_validate(response)


def create_schedule_override(schedule_id: str, override_request: ScheduleOverrideCreate) -> dict | list:
    """Create an override for a schedule.

    Args:
        schedule_id: The ID of the schedule to override
        override_request: Data for the schedule override

    Returns:
        The created schedule override
    """
    json_data = override_request.model_dump()

    # Convert datetime objects to ISO format strings for API compatibility
    for i, override in enumerate(json_data["overrides"]):
        original_override = override_request.overrides[i]
        override["start"] = original_override.start.isoformat()
        override["end"] = original_override.end.isoformat()

    return get_client().rpost(f"/schedules/{schedule_id}/overrides", json=json_data)


def list_schedule_users(schedule_id: str) -> ListResponseModel[User]:
    """List users in a schedule.

    Args:
        schedule_id: The ID of the schedule

    Returns:
        List of users in the schedule
    """
    response = get_client().rget(f"/schedules/{schedule_id}/users")
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)
