import logging
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.schedules_v3 import (
    CustomShift,
    CustomShiftCreate,
    CustomShiftUpdate,
    OverrideShift,
    OverrideShiftCreate,
    OverrideShiftUpdate,
    Rotation,
    RotationEvent,
    RotationEventCreate,
    RotationEventUpdate,
    ScheduleV3,
    ScheduleV3Create,
    ScheduleV3Update,
    ShiftMember,
)

logger = logging.getLogger(__name__)

# The pagerduty SDK's rget/rpost/rput/rdelete validate paths against a hardcoded
# CANONICAL_PATHS allowlist. /v3/schedules is a newer API path not included in
# that list. We use client.get/post/put directly (which goes through the underlying
# requests.Session with auth headers) and construct the full URL ourselves.


def _v3_url(client: Any, path: str) -> str:
    """Build a full v3 API URL from a relative path."""
    return f"{client.url}{path}"


def _unwrap(response: Any, key: str) -> dict:
    """Extract a resource dict from API response, handling both wrapped and unwrapped forms."""
    if isinstance(response, dict) and key in response:
        return response[key]
    return response


def _unwrap_list(response: Any, key: str) -> list:
    """Extract a list of resources from API response."""
    if isinstance(response, dict) and key in response:
        return response[key]
    if isinstance(response, list):
        return response
    return []


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

    Rotations can be embedded in the create payload, or added afterwards with
    create_schedule_v3_rotation and create_schedule_v3_rotation_event.

    Args:
        schedule_data: Data for the new v3 schedule, including name and time_zone (required),
            plus optional description, teams, and rotations

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

    To manage rotation events, custom shifts, or overrides incrementally, use the
    dedicated tools for those sub-resources. Note the API requires time_zone on
    every update, even when changing unrelated fields.

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


def delete_schedule_v3(schedule_id: str) -> str:
    """Delete a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule to delete

    Returns:
        Confirmation message
    """
    client = get_client()
    resp = client.delete(_v3_url(client, f"/v3/schedules/{schedule_id}"))
    _check_v3_response(resp)
    return f"Schedule {schedule_id} deleted successfully."


# ---- Rotation tools ----


def list_schedule_v3_rotations(schedule_id: str) -> ListResponseModel[Rotation]:
    """List all rotations for a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule

    Returns:
        List of rotations for the schedule
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/rotations"))
    _check_v3_response(resp)
    raw = _unwrap_list(resp.json(), "rotations")
    return ListResponseModel[Rotation](response=[Rotation(**r) for r in raw])


def create_schedule_v3_rotation(schedule_id: str) -> Rotation:
    """Create a new rotation within a v3 schedule.

    Rotations are containers for events. After creating a rotation, add events to it
    using create_schedule_v3_rotation_event to define on-call coverage windows and members.

    Args:
        schedule_id: The ID of the v3 schedule to add the rotation to

    Returns:
        The created rotation
    """
    client = get_client()
    resp = client.post(
        _v3_url(client, f"/v3/schedules/{schedule_id}/rotations"),
        json={},
    )
    _check_v3_response(resp)
    return Rotation.model_validate(_unwrap(resp.json(), "rotation"))


def get_schedule_v3_rotation(schedule_id: str, rotation_id: str) -> Rotation:
    """Get a specific rotation within a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation

    Returns:
        The rotation including its events
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}"))
    _check_v3_response(resp)
    return Rotation.model_validate(_unwrap(resp.json(), "rotation"))


def delete_schedule_v3_rotation(schedule_id: str, rotation_id: str) -> str:
    """Delete a rotation from a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation to delete

    Returns:
        Confirmation message
    """
    client = get_client()
    resp = client.delete(_v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}"))
    _check_v3_response(resp)
    return f"Rotation {rotation_id} deleted from schedule {schedule_id}."


# ---- Rotation event tools ----


def list_schedule_v3_rotation_events(schedule_id: str, rotation_id: str) -> ListResponseModel[RotationEvent]:
    """List all events for a rotation in a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation

    Returns:
        List of events defining the on-call coverage windows and member assignments
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}/events"))
    _check_v3_response(resp)
    raw = _unwrap_list(resp.json(), "events")
    return ListResponseModel[RotationEvent](response=[RotationEvent(**e) for e in raw])


def create_schedule_v3_rotation_event(
    schedule_id: str,
    rotation_id: str,
    event_data: RotationEventCreate,
) -> RotationEvent:
    """Create a new event within a v3 schedule rotation.

    An event defines when and how users are on-call: the recurring time window
    (start_time/end_time), a recurrence rule (RRULE), and an assignment strategy
    (rotating or every-member).

    Example for a weekly rotating on-call:
      name: "Weekly On-Call"
      start_time: {date_time: "2025-03-03T09:00:00Z", time_zone: "America/New_York"}
      end_time: {date_time: "2025-03-10T09:00:00Z", time_zone: "America/New_York"}
      effective_since: "2025-03-03T09:00:00Z"
      recurrence: ["RRULE:FREQ=WEEKLY"]
      assignment_strategy:
        type: "rotating_member_assignment_strategy"
        shifts_per_member: 1
        members:
          - {type: "user_member", user_id: "PUSER123"}
          - {type: "user_member", user_id: "PUSER456"}

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation to add this event to
        event_data: Event configuration including name, time window, recurrence, and assignment strategy

    Returns:
        The created rotation event
    """
    client = get_client()
    payload = {"event": event_data.model_dump(exclude_none=True)}
    resp = client.post(
        _v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}/events"),
        json=payload,
    )
    _check_v3_response(resp)
    return RotationEvent.model_validate(_unwrap(resp.json(), "event"))


def get_schedule_v3_rotation_event(schedule_id: str, rotation_id: str, event_id: str) -> RotationEvent:
    """Get a specific event within a v3 schedule rotation.

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation
        event_id: The ID of the event

    Returns:
        The rotation event
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}/events/{event_id}"))
    _check_v3_response(resp)
    return RotationEvent.model_validate(_unwrap(resp.json(), "event"))


def update_schedule_v3_rotation_event(
    schedule_id: str,
    rotation_id: str,
    event_id: str,
    event_data: RotationEventUpdate,
) -> RotationEvent:
    """Update an existing rotation event in a v3 schedule.

    Update rules:
    - Active events (already started): only effective_until can be changed
    - Future events: all fields can be changed
    - Past events: cannot be changed (returns 400)

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation
        event_id: The ID of the event to update
        event_data: Fields to update (only provided fields are changed)

    Returns:
        The updated rotation event
    """
    client = get_client()
    payload = {"event": event_data.model_dump(exclude_none=True)}
    resp = client.put(
        _v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}/events/{event_id}"),
        json=payload,
    )
    _check_v3_response(resp)
    return RotationEvent.model_validate(_unwrap(resp.json(), "event"))


def delete_schedule_v3_rotation_event(schedule_id: str, rotation_id: str, event_id: str) -> str:
    """Delete an event from a v3 schedule rotation.

    Args:
        schedule_id: The ID of the v3 schedule
        rotation_id: The ID of the rotation
        event_id: The ID of the event to delete

    Returns:
        Confirmation message
    """
    client = get_client()
    resp = client.delete(_v3_url(client, f"/v3/schedules/{schedule_id}/rotations/{rotation_id}/events/{event_id}"))
    _check_v3_response(resp)
    return f"Event {event_id} deleted from rotation {rotation_id}."


# ---- Custom shift tools ----


def list_schedule_v3_custom_shifts(
    schedule_id: str,
    since: str,
    until: str,
) -> ListResponseModel[CustomShift]:
    """List custom shifts for a v3 schedule within a time range.

    Custom shifts are ad-hoc one-off shifts outside of rotation events.

    Args:
        schedule_id: The ID of the v3 schedule
        since: Start of the time range (ISO 8601, required)
        until: End of the time range (ISO 8601, required)

    Returns:
        List of custom shifts in the specified time range
    """
    client = get_client()
    params = {"since": since, "until": until}
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/custom_shifts"), params=params)
    _check_v3_response(resp)
    raw = _unwrap_list(resp.json(), "custom_shifts")
    return ListResponseModel[CustomShift](response=[CustomShift(**s) for s in raw])


def create_schedule_v3_custom_shifts(
    schedule_id: str,
    custom_shifts: list[CustomShiftCreate],
) -> ListResponseModel[CustomShift]:
    """Create one or more custom shifts for a v3 schedule.

    Custom shifts are ad-hoc one-off shifts that sit outside of rotation events,
    useful for covering specific dates without modifying the rotation.

    Example:
      custom_shifts:
        - type: "custom_shift"
          start_time: "2025-03-15T09:00:00Z"
          end_time: "2025-03-15T17:00:00Z"
          assignments:
            - type: "shift_assignment"
              member: {type: "user_member", user_id: "PUSER123"}

    Args:
        schedule_id: The ID of the v3 schedule
        custom_shifts: List of custom shifts to create

    Returns:
        The created custom shifts
    """
    client = get_client()
    payload = {"custom_shifts": [s.model_dump(exclude_none=True) for s in custom_shifts]}
    resp = client.post(_v3_url(client, f"/v3/schedules/{schedule_id}/custom_shifts"), json=payload)
    _check_v3_response(resp)
    raw = _unwrap_list(resp.json(), "custom_shifts")
    return ListResponseModel[CustomShift](response=[CustomShift(**s) for s in raw])


def get_schedule_v3_custom_shift(schedule_id: str, custom_shift_id: str) -> CustomShift:
    """Get a specific custom shift within a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        custom_shift_id: The ID of the custom shift

    Returns:
        The custom shift
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/custom_shifts/{custom_shift_id}"))
    _check_v3_response(resp)
    return CustomShift.model_validate(_unwrap(resp.json(), "custom_shift"))


def update_schedule_v3_custom_shift(
    schedule_id: str,
    custom_shift_id: str,
    shift_data: CustomShiftUpdate,
) -> CustomShift:
    """Update an existing custom shift in a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        custom_shift_id: The ID of the custom shift to update
        shift_data: Fields to update

    Returns:
        The updated custom shift
    """
    client = get_client()
    payload = {"custom_shift": shift_data.model_dump(exclude_none=True)}
    resp = client.put(
        _v3_url(client, f"/v3/schedules/{schedule_id}/custom_shifts/{custom_shift_id}"),
        json=payload,
    )
    _check_v3_response(resp)
    return CustomShift.model_validate(_unwrap(resp.json(), "custom_shift"))


def delete_schedule_v3_custom_shift(schedule_id: str, custom_shift_id: str) -> str:
    """Delete a custom shift from a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        custom_shift_id: The ID of the custom shift to delete

    Returns:
        Confirmation message
    """
    client = get_client()
    resp = client.delete(_v3_url(client, f"/v3/schedules/{schedule_id}/custom_shifts/{custom_shift_id}"))
    _check_v3_response(resp)
    return f"Custom shift {custom_shift_id} deleted from schedule {schedule_id}."


# ---- Override tools ----


def list_schedule_v3_overrides(
    schedule_id: str,
    since: str,
    until: str,
) -> ListResponseModel[OverrideShift]:
    """List overrides for a v3 schedule within a time range.

    Args:
        schedule_id: The ID of the v3 schedule
        since: Start of the time range (ISO 8601, required)
        until: End of the time range (ISO 8601, required)

    Returns:
        List of overrides in the specified time range
    """
    client = get_client()
    params = {"since": since, "until": until}
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/overrides"), params=params)
    _check_v3_response(resp)
    raw = _unwrap_list(resp.json(), "overrides")
    return ListResponseModel[OverrideShift](response=[OverrideShift(**o) for o in raw])


def create_schedule_v3_overrides(
    schedule_id: str,
    overrides: list[OverrideShiftCreate],
) -> ListResponseModel[OverrideShift]:
    """Create one or more overrides for a v3 schedule.

    An override temporarily replaces a scheduled on-call member with a different
    member for a specific time period. Each override must reference either a
    rotation_id or a custom_shift_id (not both).

    Example:
      overrides:
        - type: "override_shift"
          rotation_id: "ROTATION_ID"
          start_time: "2025-03-15T09:00:00Z"
          end_time: "2025-03-15T17:00:00Z"
          overridden_member: {type: "user_member", user_id: "PUSER123"}
          overriding_member: {type: "user_member", user_id: "PUSER456"}

    Args:
        schedule_id: The ID of the v3 schedule
        overrides: List of overrides to create

    Returns:
        The created overrides
    """
    client = get_client()
    payload = {"overrides": [o.model_dump(exclude_none=True) for o in overrides]}
    resp = client.post(_v3_url(client, f"/v3/schedules/{schedule_id}/overrides"), json=payload)
    _check_v3_response(resp)
    raw = _unwrap_list(resp.json(), "overrides")
    return ListResponseModel[OverrideShift](response=[OverrideShift(**o) for o in raw])


def get_schedule_v3_override(schedule_id: str, override_id: str) -> OverrideShift:
    """Get a specific override within a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        override_id: The ID of the override

    Returns:
        The override
    """
    client = get_client()
    resp = client.get(_v3_url(client, f"/v3/schedules/{schedule_id}/overrides/{override_id}"))
    _check_v3_response(resp)
    return OverrideShift.model_validate(_unwrap(resp.json(), "override"))


def update_schedule_v3_override(
    schedule_id: str,
    override_id: str,
    start_time: str,
    end_time: str,
    overridden_member_type: str,
    overriding_member_type: str,
    overridden_member_user_id: str | None = None,
    overriding_member_user_id: str | None = None,
) -> OverrideShift:
    """Update an existing override in a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        override_id: The ID of the override to update
        start_time: ISO 8601 start datetime of the override
        end_time: ISO 8601 end datetime of the override
        overridden_member_type: Type of the member being replaced — 'user_member' or 'empty_member'
        overriding_member_type: Type of the member taking over — 'user_member' or 'empty_member'
        overridden_member_user_id: PagerDuty user ID of the member being replaced (required when type is 'user_member')
        overriding_member_user_id: PagerDuty user ID of the member taking over (required when type is 'user_member')

    Returns:
        The updated override
    """
    override_data = OverrideShiftUpdate(
        start_time=start_time,
        end_time=end_time,
        overridden_member=ShiftMember(type=overridden_member_type, user_id=overridden_member_user_id),
        overriding_member=ShiftMember(type=overriding_member_type, user_id=overriding_member_user_id),
    )
    client = get_client()
    payload = {"override": override_data.model_dump(exclude_none=True)}
    resp = client.put(
        _v3_url(client, f"/v3/schedules/{schedule_id}/overrides/{override_id}"),
        json=payload,
    )
    _check_v3_response(resp)
    return OverrideShift.model_validate(_unwrap(resp.json(), "override"))


def delete_schedule_v3_override(schedule_id: str, override_id: str) -> str:
    """Delete an override from a v3 schedule.

    Args:
        schedule_id: The ID of the v3 schedule
        override_id: The ID of the override to delete

    Returns:
        Confirmation message
    """
    client = get_client()
    resp = client.delete(_v3_url(client, f"/v3/schedules/{schedule_id}/overrides/{override_id}"))
    _check_v3_response(resp)
    return f"Override {override_id} deleted from schedule {schedule_id}."
