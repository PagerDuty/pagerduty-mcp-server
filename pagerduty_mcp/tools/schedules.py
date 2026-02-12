from pagerduty_mcp.models import (
    ListResponseModel,
    MCPContext,
    Schedule,
    ScheduleCreateRequest,
    ScheduleOverrideCreate,
    ScheduleQuery,
    ScheduleUpdateRequest,
    User,
)
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def list_schedules(query_model: ScheduleQuery, context: MCPContext) -> ListResponseModel[Schedule]:
    """List schedules with optional filtering.

    Args:
        query_model: Optional filtering parameters
        context: The MCP context with client and user info (injected)

    Returns:
        List of schedules matching the query parameters
    """
    response = paginate(client=context.client, entity="schedules", params=query_model.to_params())
    schedules = [Schedule(**schedule) for schedule in response]
    return ListResponseModel[Schedule](response=schedules)


@inject_context
def get_schedule(schedule_id: str, context: MCPContext) -> Schedule:
    """Get a specific schedule by ID.

    Args:
        schedule_id: The ID of the schedule to retrieve
        context: The MCP context with client and user info (injected)

    Returns:
        Schedule details
    """
    response = context.client.rget(f"/schedules/{schedule_id}")
    return Schedule.from_api_response(response)


@inject_context
def create_schedule_override(schedule_id: str, override_request: ScheduleOverrideCreate, context: MCPContext) -> dict | list:
    """Create an override for a schedule.

    Args:
        schedule_id: The ID of the schedule to override
        override_request: Data for the schedule override
        context: The MCP context with client and user info (injected)

    Returns:
        The created schedule override
    """
    request_data = override_request.model_dump()
    for override in request_data["overrides"]:
        override["start"] = override["start"].isoformat()
        override["end"] = override["end"].isoformat()

    return context.client.rpost(f"/schedules/{schedule_id}/overrides", json=request_data)


@inject_context
def list_schedule_users(schedule_id: str, context: MCPContext) -> ListResponseModel[User]:
    """List users in a schedule.

    Args:
        schedule_id: The ID of the schedule
        context: The MCP context with client and user info (injected)

    Returns:
        List of users in the schedule
    """
    response = context.client.rget(f"/schedules/{schedule_id}/users")
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)


@inject_context
def create_schedule(create_model: ScheduleCreateRequest, context: MCPContext) -> Schedule:
    """Create a new on-call schedule.

    Args:
        create_model: The schedule creation data
        context: The MCP context with client and user info (injected)

    Returns:
        The created schedule
    """
    request_data = create_model.model_dump()
    for layer in request_data["schedule"]["schedule_layers"]:
        layer["start"] = layer["start"].isoformat()
        if layer["end"] is not None:
            layer["end"] = layer["end"].isoformat()
        layer["rotation_virtual_start"] = layer["rotation_virtual_start"].isoformat()

        restrictions = layer.get("restrictions", [])
        if restrictions is not None:
            for restriction in restrictions:
                if "start_day_of_week" not in restriction or restriction["start_day_of_week"] is None:
                    restriction["start_day_of_week"] = 1

    response = context.client.rpost("/schedules", json=request_data)
    return Schedule.from_api_response(response)


@inject_context
def update_schedule(schedule_id: str, update_model: ScheduleUpdateRequest, context: MCPContext) -> Schedule:
    """Update an existing schedule.

    Args:
        schedule_id: The ID of the schedule to update
        update_model: The updated schedule data
        context: The MCP context with client and user info (injected)

    Returns:
        The updated schedule
    """
    request_data = update_model.model_dump()

    if len(request_data["schedule"]["schedule_layers"]) > 0:
        for layer in request_data["schedule"]["schedule_layers"]:
            layer["start"] = layer["start"].isoformat()
            if layer["end"] is not None:
                layer["end"] = layer["end"].isoformat()
            layer["rotation_virtual_start"] = layer["rotation_virtual_start"].isoformat()

            restrictions = layer.get("restrictions", [])
            if restrictions is not None:
                for restriction in restrictions:
                    if "start_day_of_week" not in restriction or restriction["start_day_of_week"] is None:
                        restriction["start_day_of_week"] = 1

    try:
        response = context.client.rput(f"/schedules/{schedule_id}", json=request_data)
        return Schedule.from_api_response(response)
    except Exception as e:
        raise Exception(f"Failed to update schedule {schedule_id}: {e!s}") from e
