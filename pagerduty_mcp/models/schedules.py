from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from pagerduty_mcp.models.base import (
    DEFAULT_PAGINATION_LIMIT,
    MAX_RESULTS,
    MAXIMUM_PAGINATION_LIMIT,
    ListResponseModel,
)
from pagerduty_mcp.models.references import TeamReference, UserReference
from pagerduty_mcp.models.schedules_v3 import ScheduleV3


class ScheduleLayerUser(BaseModel):
    user: UserReference = Field(description="The reference to the user in this layer")


class ScheduleLayer(BaseModel):
    id: str = Field(description="The ID of the schedule layer")
    start: datetime = Field(description="The start time of this layer")
    end: datetime | None = Field(
        default=None,
        description="The end time of this layer. If null, the layer does not end",
    )
    name: str = Field(description="The name of the schedule layer")
    rotation_virtual_start: datetime = Field(
        description="The effective start time of the layer. This can be before the start time of the schedule"
    )
    rotation_turn_length_seconds: int = Field(description="The duration of each on-call shift in seconds")
    users: list[ScheduleLayerUser] = Field(
        description="The ordered list of users on this layer. The position of the user on the list"
        " determines their order in the layer"
    )
    restrictions: list[dict[str, Any]] | None = Field(
        default=None,
        description="An array of restrictions for the layer. A restriction is a limit on which"
        " period of the day or week the schedule layer can accept assignments",
    )


class Schedule(BaseModel):
    # Normalized discriminator shared with ScheduleV3 so both can live in a single
    # discriminated union (ScheduleDetail) without collapsing their distinct shapes.
    kind: Literal["layer_based"] = Field(
        default="layer_based",
        description="Identifies this as a classic layer-based (v2) schedule",
    )
    id: str | None = Field(description="The ID of the schedule", default=None)
    summary: str = Field(
        description="A short-form, server-generated string that provides succinct information about the schedule"
    )
    name: str = Field(description="The name of the schedule")
    description: str | None = Field(default=None, description="The description of the schedule")
    time_zone: str = Field(description="The time zone of the schedule")
    self_url: str | None = Field(default=None, description="The API URL at which this schedule is accessible")
    html_url: str | None = Field(
        default=None,
        description="The URL at which this schedule is accessible in the PagerDuty UI",
    )
    created_at: datetime | None = Field(default=None, description="The date/time when this schedule was created")
    updated_at: datetime | None = Field(default=None, description="The date/time when this schedule was last updated")
    users: list[UserReference] | None = Field(default=None, description="The users associated with this schedule")
    teams: list[TeamReference] | None = Field(default=None, description="The teams associated with this schedule")
    schedule_layers: list[ScheduleLayer] | None = Field(
        default=None, description="A list of schedule layers for this schedule"
    )

    @computed_field
    @property
    def type(self) -> Literal["schedule"]:
        return "schedule"

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any] | list | None) -> "Schedule":
        """Create Schedule from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Wrapped: {"schedule": {...}}
        - Direct: {...} (schedule data directly)

        Args:
            response_data: The API response data

        Returns:
            Schedule instance
        """
        if isinstance(response_data, dict) and "schedule" in response_data:
            return cls.model_validate(response_data["schedule"])

        return cls.model_validate(response_data)


class ScheduleQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str | None = Field(description="Filter schedules by name or description", default=None)
    team_ids: list[str] | None = Field(description="Filter schedules by team IDs", default=None)
    user_ids: list[str] | None = Field(description="Filter schedules by user IDs", default=None)
    include: list[str] | None = Field(
        description="Include additional details in response, such as 'schedule_layers'",
        default=None,
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.query:
            params["query"] = self.query
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.user_ids:
            params["user_ids[]"] = self.user_ids
        if self.include:
            params["include[]"] = self.include
        if self.limit:
            params["limit"] = self.limit
        return params


class Override(BaseModel):
    start: datetime = Field(description="The start time of the override")
    end: datetime = Field(description="The end time of the override")
    user_id: str = Field(description="The ID of the user for this override")


class ScheduleOverrideCreate(BaseModel):
    overrides: list[Override] = Field(description="The list of overrides to create for the schedule")


class ScheduleLayerRestriction(BaseModel):
    type: str = Field(description="The type of restriction (daily_restriction or weekly_restriction)")
    start_time_of_day: str = Field(description="The time of day when the restriction starts (HH:MM:SS)")
    duration_seconds: int = Field(description="The duration of the restriction in seconds")
    start_day_of_week: int = Field(
        default=1,
        description="The day of week the restriction starts (1=Monday, 7=Sunday, ISO-8601)",
    )


class ScheduleLayerCreate(BaseModel):
    name: str = Field(description="The name of the schedule layer")
    start: datetime = Field(description="The start time of this layer")
    end: datetime | None = Field(
        default=None,
        description="The end time of this layer. If null, the layer does not end",
    )
    rotation_virtual_start: datetime = Field(
        description="The effective start time of the layer. This can be before the start time of the schedule"
    )
    rotation_turn_length_seconds: int = Field(description="The duration of each on-call shift in seconds")
    users: list[ScheduleLayerUser] = Field(
        description="The ordered list of users on this layer. The position of the user on the list "
        "determines their order in the layer"
    )
    restrictions: list[ScheduleLayerRestriction] | None = Field(
        default=None,
        description="An array of restrictions for the layer. A restriction is a limit on which "
        "period of the day or week the schedule layer can accept assignments",
    )


class ScheduleCreateData(BaseModel):
    name: str = Field(description="The name of the schedule")
    time_zone: str = Field(
        description="The time zone of the schedule using IANA timezone format (e.g., 'America/New_York')"
    )
    description: str | None = Field(default=None, description="The description of the schedule")
    schedule_layers: list[ScheduleLayerCreate] = Field(description="A list of schedule layers")
    type: Literal["schedule"] = "schedule"


class ScheduleCreateRequest(BaseModel):
    schedule: ScheduleCreateData = Field(
        description="The schedule to be created",
    )


class ScheduleUpdateRequest(BaseModel):
    schedule: ScheduleCreateData = Field(description="The updated schedule data")
    id: str | None = Field(default=None, description="The ID of the schedule to update (optional if provided in path)")


# A single schedule of either system. The "kind" discriminator lets callers (and the LLM)
# tell a classic layer-based (v2) schedule from a next-gen shift-based (v3) one, and lets
# downstream code build the correct escalation-policy target type.
ScheduleDetail = Annotated[Schedule | ScheduleV3, Field(discriminator="kind")]


class ScheduleSummary(BaseModel):
    """A lightweight schedule entry returned by the unified list_schedules tool.

    Both schedule systems are represented uniformly here; the "kind" field tells them apart.
    Shift-based (v3) names are filled in by enrichment when available (see list_schedules).
    """

    id: str = Field(description="The ID of the schedule")
    name: str | None = Field(
        default=None,
        description="The schedule name. May be null for a shift-based (v3) schedule when enrichment is disabled",
    )
    kind: Literal["layer_based", "shift_based"] = Field(
        description="Which scheduling system this belongs to: classic layer-based (v2) or next-gen shift-based (v3)"
    )
    time_zone: str | None = Field(default=None, description="The time zone of the schedule")
    html_url: str | None = Field(
        default=None, description="The URL at which this schedule is accessible in the PagerDuty UI"
    )
    summary: str | None = Field(default=None, description="A short-form, server-generated summary of the schedule")


class SourceStatus(BaseModel):
    """Per-API outcome for one half of a unified schedules listing."""

    api: Literal["v2", "v3"] = Field(description="Which schedules API this status refers to")
    status: Literal["ok", "error"] = Field(description="Whether this source was retrieved successfully")
    count: int = Field(default=0, description="Number of schedules returned from this source")
    more: bool = Field(default=False, description="Whether this source has additional pages not included")
    message: str | None = Field(default=None, description="Error detail (on failure) or an informational note")


class SchedulesListResponse(ListResponseModel[ScheduleSummary]):
    """Unified schedules list spanning BOTH the layer-based (v2) and shift-based (v3) systems.

    `sources` and `degraded` exist so a partial failure can NEVER be mistaken for a complete
    answer: if one system fails, the other's results are still returned but the response is
    explicitly marked incomplete.
    """

    sources: list[SourceStatus] = Field(
        default_factory=list, description="Per-API retrieval status for each scheduling system"
    )
    degraded: bool = Field(default=False, description="True if any source failed; the list is then INCOMPLETE")

    @computed_field
    @property
    def response_summary(self) -> str:
        count = len(self.response)
        n_v2 = sum(s.count for s in self.sources if s.api == "v2" and s.status == "ok")
        n_v3 = sum(s.count for s in self.sources if s.api == "v3" and s.status == "ok")
        lines = [
            "ListResponseModel<ScheduleSummary>:",
            f"- Returned {count} schedule(s): {n_v2} layer-based (v2), {n_v3} shift-based (v3).",
        ]
        for source in self.sources:
            label = "layer-based (v2)" if source.api == "v2" else "shift-based (v3)"
            if source.status == "error":
                lines.append(
                    f"- WARNING: the {label} source FAILED — this list is INCOMPLETE."
                    f" Do not tell the user these schedules do not exist. ({source.message})"
                )
            elif source.message:
                lines.append(f"- Note ({label}): {source.message}")
            elif source.more:
                lines.append(f"- Note: more {label} schedules exist beyond the returned page.")
        if count >= MAX_RESULTS:
            lines.append("- WARNING: the number of records equals the response limit; there may be more not included.")
        return "\n".join(lines)
