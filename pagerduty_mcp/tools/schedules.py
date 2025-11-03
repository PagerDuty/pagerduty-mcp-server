from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Schedule,
    ScheduleCreateRequest,
    ScheduleOverrideCreate,
    ScheduleQuery,
    ScheduleUpdateRequest,
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
    if isinstance(response, dict) and "schedule" in response:
        return Schedule.model_validate(response["schedule"])

    return Schedule.model_validate(response)


def update_schedule(schedule_id: str, update_model: ScheduleUpdateRequest) -> Schedule:
    """Update an existing schedule.

    This function updates a PagerDuty schedule. For basic property updates (name, description, etc.),
    you can provide these properties while setting schedule_layers to an empty list to preserve
    existing layers.

    For complete schedule updates, including modifying layers, you must include all existing layers
    that should be preserved, as the PagerDuty API replaces all layers with those provided.

    Args:
        schedule_id: The ID of the schedule to update (e.g., 'P5V4UJK')
        update_model: The updated schedule data. Must be a ScheduleUpdateRequest object containing:
            - schedule: (REQUIRED) ScheduleCreateData with:
                - name: (REQUIRED) Schedule name
                - time_zone: (REQUIRED) IANA timezone (e.g., 'America/New_York')
                - schedule_layers: (REQUIRED) List of layers or empty list []
                - description: (OPTIONAL) Schedule description

    Returns:
        The updated schedule

    Raises:
        Exception: If the API request fails with a detailed error message including the schedule_id

    Example:
        >>> from pagerduty_mcp.models import ScheduleUpdateRequest, ScheduleCreateData
        >>> update_data = ScheduleCreateData(
        ...     name="Updated Schedule",
        ...     time_zone="America/New_York",
        ...     schedule_layers=[]  # Empty to preserve existing layers
        ... )
        >>> request = ScheduleUpdateRequest(schedule=update_data)
        >>> result = update_schedule("P5V4UJK", request)
    """
    # Start by getting current schedule if we need to handle empty layers
    request_data = update_model.model_dump()

    # Check if this is a partial update (empty schedule_layers)
    if len(request_data["schedule"]["schedule_layers"]) == 0:
        # For partial updates with empty layers, we're only updating basic properties
        # and want to preserve existing layers, so we don't need to process layers
        pass
    else:
        # Process datetime objects for schedule layers
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

    try:
        # Send request to PagerDuty API
        response = get_client().rput(f"/schedules/{schedule_id}", json=request_data)

        # Handle different response formats
        if isinstance(response, dict) and "schedule" in response:
            return Schedule.model_validate(response["schedule"])

        return Schedule.model_validate(response)
    except Exception as e:
        # Re-raise with more detailed error message
        error_msg = str(e)
        raise Exception(f"Failed to update schedule {schedule_id}: {error_msg}") from e


def get_layer_differences(existing_schedule: Schedule, new_layers: list) -> dict:
    """Compare existing schedule layers with new layers to identify changes.

    Args:
        existing_schedule: Current schedule with existing layers
        new_layers: List of new layer definitions to compare against

    Returns:
        Dictionary with added, modified, and removed layers
    """
    existing_layers = existing_schedule.schedule_layers or []

    # Track layers by ID
    existing_by_id = {layer.id: layer for layer in existing_layers if layer.id}
    new_by_id = {layer.get("id"): layer for layer in new_layers if layer.get("id")}

    # Find added, modified, and removed layers
    added = []
    modified = []
    removed = []

    # Identify modified layers (have same ID but different properties)
    for layer_id, new_layer in new_by_id.items():
        if layer_id in existing_by_id:
            # Layer exists - need to check if it's actually modified
            modified.append(new_layer)

    # Identify added layers (no ID, or ID not in existing)
    for layer in new_layers:
        layer_id = layer.get("id")
        if not layer_id or layer_id not in existing_by_id:
            added.append(layer)

    # Identify removed layers (in existing but not in new)
    for layer_id, existing_layer in existing_by_id.items():
        if layer_id not in new_by_id:
            removed.append(existing_layer)

    return {"added": added, "modified": modified, "removed": removed}
