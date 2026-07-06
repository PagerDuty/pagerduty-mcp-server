from typing import Any, Literal

from pydantic import BaseModel, Field


class ScheduleV3(BaseModel):
    """A PagerDuty v3 schedule (next-gen, shift-based scheduling system)."""

    # Normalized discriminator shared with the v2 Schedule model so both can live in a
    # single discriminated union (ScheduleDetail) without losing their distinct shapes.
    kind: Literal["shift_based"] = Field(
        default="shift_based",
        description="Identifies this as a next-gen shift-based (v3) schedule",
    )
    id: str | None = Field(default=None, description="The ID of the v3 schedule")
    name: str | None = Field(default=None, description="The name of the v3 schedule")
    description: str | None = Field(default=None, description="A description of the v3 schedule")
    time_zone: str | None = Field(default=None, description="The time zone of the v3 schedule (e.g. America/New_York)")
    type: str | None = Field(default=None, description="The type identifier for the schedule")
    summary: str | None = Field(default=None, description="A short-form summary of the v3 schedule")
    teams: list[dict[str, Any]] | None = Field(default=None, description="Teams associated with this schedule")
    rotations: list[dict[str, Any]] | None = Field(
        default=None, description="Rotations configured for this v3 schedule"
    )
    html_url: str | None = Field(
        default=None, description="The URL at which this v3 schedule is accessible in the PagerDuty UI"
    )


class ScheduleV3Create(BaseModel):
    """Request body for creating a v3 schedule."""

    name: str = Field(description="The name of the v3 schedule")
    description: str | None = Field(default=None, description="A description of the v3 schedule")
    time_zone: str = Field(description="The time zone for the v3 schedule (e.g. America/New_York)")
    teams: list[dict[str, Any]] | None = Field(
        default=None, description="Teams to associate with this schedule (each must have an 'id' field)"
    )
    rotations: list[dict[str, Any]] | None = Field(
        default=None,
        description=(
            "Rotations for the schedule. Each rotation contains events, which contain "
            "custom_shifts that define on-call coverage windows."
        ),
    )


class ScheduleV3Update(BaseModel):
    """Request body for updating a v3 schedule."""

    name: str | None = Field(default=None, description="The updated name of the v3 schedule")
    description: str | None = Field(default=None, description="The updated description of the v3 schedule")
    time_zone: str | None = Field(default=None, description="The updated time zone for the v3 schedule")
    teams: list[dict[str, Any]] | None = Field(
        default=None, description="Updated teams to associate with this schedule"
    )
    rotations: list[dict[str, Any]] | None = Field(default=None, description="Updated rotations for the v3 schedule")


# --- Rotation models ---


class Rotation(BaseModel):
    """A rotation within a v3 schedule. Scheduling logic is defined on the rotation's events."""

    id: str | None = Field(default=None, description="The ID of the rotation")
    type: str | None = Field(default=None, description="Resource type identifier")
    events: list[dict[str, Any]] | None = Field(default=None, description="Events in this rotation")
    self: str | None = Field(default=None, description="API URL for this rotation")
    html_url: str | None = Field(default=None, description="PagerDuty UI URL for this rotation")


# --- Rotation event models ---


class ZonedDateTime(BaseModel):
    """A time-of-day value with an explicit time zone."""

    date_time: str = Field(description="ISO 8601 datetime string (e.g. 2025-03-03T09:00:00Z)")
    time_zone: str = Field(description="IANA timezone identifier (e.g. America/New_York)")


class ShiftMember(BaseModel):
    """A member (user) assigned to a shift or rotation slot."""

    type: Literal["user_member", "empty_member"] = Field(
        description="'user_member' for a specific user, 'empty_member' for an intentionally unassigned slot"
    )
    user_id: str | None = Field(default=None, description="The PagerDuty user ID. Required when type is 'user_member'")


class AssignmentStrategy(BaseModel):
    """Defines how users are assigned on-call within a rotation event's time window."""

    type: Literal["rotating_member_assignment_strategy", "every_member_assignment_strategy"] = Field(
        description=(
            "'rotating_member_assignment_strategy': users rotate in sequence. "
            "'every_member_assignment_strategy': all members are on-call simultaneously."
        )
    )
    members: list[ShiftMember] = Field(
        description="List of members (up to 20). Each must have 'type' and optionally 'user_id'."
    )
    shifts_per_member: int | None = Field(
        default=None,
        description=(
            "Required for rotating_member_assignment_strategy. "
            "Number of consecutive shift occurrences each member covers before rotating."
        ),
    )


class RotationEvent(BaseModel):
    """A recurring on-call event within a rotation."""

    id: str | None = Field(default=None, description="The ID of the rotation event")
    type: str | None = Field(default=None, description="Resource type identifier")
    name: str | None = Field(default=None, description="Display name for this event")
    start_time: dict[str, Any] | None = Field(default=None, description="ZonedDateTime: {date_time, time_zone}")
    end_time: dict[str, Any] | None = Field(default=None, description="ZonedDateTime: {date_time, time_zone}")
    effective_since: str | None = Field(
        default=None, description="ISO 8601 datetime when this event starts producing shifts"
    )
    effective_until: str | None = Field(
        default=None, description="ISO 8601 datetime when this event stops producing shifts. Null means indefinite."
    )
    recurrence: list[str] | None = Field(
        default=None, description="RFC 5545 recurrence rules (e.g. ['RRULE:FREQ=WEEKLY'])"
    )
    assignment_strategy: dict[str, Any] | None = Field(default=None, description="How users are assigned on-call")
    self: str | None = Field(default=None, description="API URL for this event")
    html_url: str | None = Field(default=None, description="PagerDuty UI URL for this event")


class RotationEventCreate(BaseModel):
    """Request body for creating a rotation event."""

    name: str = Field(description="Display name for this event (max 255 characters)")
    start_time: ZonedDateTime = Field(
        description="Start of the recurring time window. Use ZonedDateTime: {date_time, time_zone}"
    )
    end_time: ZonedDateTime = Field(
        description="End of the recurring time window. Use ZonedDateTime: {date_time, time_zone}"
    )
    effective_since: str = Field(
        description="ISO 8601 datetime when this event starts producing shifts (e.g. '2025-03-03T09:00:00Z')"
    )
    effective_until: str | None = Field(
        default=None,
        description="ISO 8601 datetime when this event stops producing shifts. Omit or null for indefinite.",
    )
    recurrence: list[str] = Field(
        description=(
            "RFC 5545 recurrence rules. Array with exactly one RRULE plus optional EXDATE/RDATE entries. "
            "Example: ['RRULE:FREQ=WEEKLY'] for weekly, ['RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR'] for weekdays."
        )
    )
    assignment_strategy: AssignmentStrategy = Field(
        description=(
            "How users are assigned on-call. Use rotating_member_assignment_strategy "
            "or every_member_assignment_strategy."
        )
    )


class RotationEventUpdate(BaseModel):
    """Request body for updating a rotation event (full replace — all fields required).

    The API performs a full replacement, so all fields from RotationEventCreate must be provided.
    Note: active events (already started) will only honour changes to effective_until;
    future events allow all fields to change; past events return 400.
    """

    name: str = Field(description="Display name for this event (max 255 characters)")
    start_time: ZonedDateTime = Field(
        description="Start of the recurring time window. Use ZonedDateTime: {date_time, time_zone}"
    )
    end_time: ZonedDateTime = Field(
        description="End of the recurring time window. Use ZonedDateTime: {date_time, time_zone}"
    )
    effective_since: str = Field(description="ISO 8601 datetime when this event starts producing shifts")
    effective_until: str | None = Field(
        default=None, description="ISO 8601 datetime when this event stops producing shifts. Null for indefinite."
    )
    recurrence: list[str] = Field(description="RFC 5545 recurrence rules. Example: ['RRULE:FREQ=WEEKLY']")
    assignment_strategy: AssignmentStrategy = Field(description="How users are assigned on-call")


# --- Custom shift models ---


class CustomShiftAssignmentCreate(BaseModel):
    """Assignment entry for a custom shift creation request."""

    type: Literal["shift_assignment"] = Field(default="shift_assignment", description="Must be 'shift_assignment'")
    member: ShiftMember = Field(description="The member to assign to this shift")


class CustomShiftCreate(BaseModel):
    """A single custom shift to create (one-off ad-hoc coverage)."""

    type: Literal["custom_shift"] = Field(default="custom_shift", description="Must be 'custom_shift'")
    start_time: str = Field(description="ISO 8601 datetime for when this shift starts (e.g. '2025-03-15T09:00:00Z')")
    end_time: str = Field(description="ISO 8601 datetime for when this shift ends (e.g. '2025-03-15T17:00:00Z')")
    assignments: list[CustomShiftAssignmentCreate] = Field(description="Exactly one assignment per custom shift")


class CustomShift(BaseModel):
    """An ad-hoc one-off shift outside of rotation events."""

    id: str | None = Field(default=None, description="The ID of the custom shift")
    type: str | None = Field(default=None, description="Resource type identifier")
    start_time: str | None = Field(default=None, description="ISO 8601 start datetime")
    end_time: str | None = Field(default=None, description="ISO 8601 end datetime")
    assignments: list[dict[str, Any]] | None = Field(default=None, description="Assignments for this shift")
    self: str | None = Field(default=None, description="API URL for this custom shift")
    html_url: str | None = Field(default=None, description="PagerDuty UI URL for this custom shift")


class CustomShiftUpdate(BaseModel):
    """Request body for updating a custom shift (full replace — all fields required)."""

    type: Literal["custom_shift"] = Field(default="custom_shift", description="Must be 'custom_shift'")
    start_time: str = Field(description="ISO 8601 start datetime")
    end_time: str = Field(description="ISO 8601 end datetime")
    assignments: list[CustomShiftAssignmentCreate] = Field(description="Assignments (exactly one per shift)")


# --- Override models ---


class OverrideShiftCreate(BaseModel):
    """A single override to create."""

    type: Literal["override_shift"] = Field(default="override_shift", description="Must be 'override_shift'")
    rotation_id: str | None = Field(
        default=None,
        description="ID of the rotation whose shift is being overridden. Mutually exclusive with custom_shift_id.",
    )
    custom_shift_id: str | None = Field(
        default=None,
        description="ID of the custom shift being overridden. Mutually exclusive with rotation_id.",
    )
    start_time: str = Field(description="ISO 8601 datetime when the override starts")
    end_time: str = Field(description="ISO 8601 datetime when the override ends")
    overridden_member: ShiftMember = Field(description="The member being replaced")
    overriding_member: ShiftMember = Field(description="The member taking over")


class OverrideShift(BaseModel):
    """An override shift (temporary replacement of a scheduled on-call member)."""

    id: str | None = Field(default=None, description="The ID of the override")
    type: str | None = Field(default=None, description="Resource type identifier")
    rotation_id: str | None = Field(default=None, description="ID of the rotation being overridden")
    custom_shift_id: str | None = Field(default=None, description="ID of the custom shift being overridden")
    start_time: str | None = Field(default=None, description="ISO 8601 start datetime of the override")
    end_time: str | None = Field(default=None, description="ISO 8601 end datetime of the override")
    overridden_member: dict[str, Any] | None = Field(default=None, description="The member being replaced")
    overriding_member: dict[str, Any] | None = Field(default=None, description="The member taking over")
    self: str | None = Field(default=None, description="API URL for this override")
    html_url: str | None = Field(default=None, description="PagerDuty UI URL for this override")


class OverrideShiftUpdate(BaseModel):
    """Request body for updating an override (full replace — all fields required)."""

    type: Literal["override_shift"] = Field(default="override_shift", description="Must be 'override_shift'")
    start_time: str = Field(description="ISO 8601 start datetime of the override")
    end_time: str = Field(description="ISO 8601 end datetime of the override")
    overridden_member: ShiftMember = Field(description="The member being replaced")
    overriding_member: ShiftMember = Field(description="The member taking over")
