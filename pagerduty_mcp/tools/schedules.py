from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Schedule,
    ScheduleCreateRequest,
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
    request_data = override_request.model_dump()
    for override in request_data["overrides"]:
        override["start"] = override["start"].isoformat()
        override["end"] = override["end"].isoformat()

    return get_client().rpost(f"/schedules/{schedule_id}/overrides", json=request_data)


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


def create_schedule(create_model: ScheduleCreateRequest) -> Schedule:
    """Create a new on-call schedule.

    Args:
        create_model: The schedule creation data

    Returns:
        The created schedule
    """
    # Convert datetime objects to ISO 8601 strings for all schedule layers
    request_data = create_model.model_dump()
    for layer in request_data["schedule"]["schedule_layers"]:
        layer["start"] = layer["start"].isoformat()
        if layer["end"] is not None:
            layer["end"] = layer["end"].isoformat()
        layer["rotation_virtual_start"] = layer["rotation_virtual_start"].isoformat()

        # Ensure all restrictions have a start_day_of_week value
        restrictions = layer.get("restrictions", [])
        if restrictions is not None:  # Handle None case for tests
            for restriction in restrictions:
                if "start_day_of_week" not in restriction or restriction["start_day_of_week"] is None:
                    restriction["start_day_of_week"] = 1  # Default to Monday

    # Send request to PagerDuty API
    response = get_client().rpost("/schedules", json=request_data)

    # Handle different response formats
    if type(response) is dict and "schedule" in response:
        return Schedule.model_validate(response["schedule"])

    return Schedule.model_validate(response)
