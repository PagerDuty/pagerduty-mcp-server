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
