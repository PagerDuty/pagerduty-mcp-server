from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.references import ChannelReference, ServiceReference, TeamReference

LogEntriesInclude = Literal["incident", "services", "channels", "teams"]


class LogEntriesQuery(BaseModel):
    include: list[LogEntriesInclude] | None = Field(
        description="Additional Models to include in response", default=None
    )
    since: datetime | None = Field(description="Filter alerts since a specific date", default=None)
    until: datetime | None = Field(description="Filter alerts until a specific date", default=None)
    team_ids: list[str] | None = Field(description="Filter alerts by team IDs", default=None)
    limit: int | None = Field(
        ge=1,
        le=MAX_RESULTS,
        default=MAX_RESULTS,
        description="Maximum number of results to return. The maximum is 1000",
    )
    sort_by: (
        list[
            Literal[
                "created_at:asc",
                "created_at:desc",
            ]
        ]
        | None
    ) = Field(
        default=None,
        description="Sort field and direction (created_at with asc/desc)",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.include:
            params["include[]"] = self.include
        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.sort_by:
            params["sort_by"] = ",".join(self.sort_by)
        return params


class GetLogEntriesQuery(BaseModel):
    include: list[LogEntriesInclude] | None = Field(
        description="Additional Models to include in response", default=["channels"]
    )
    time_zone: str | None = Field(
        description="Time zone in which dates should be rendered (e.g., 'America/New_York')", default=None
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.include:
            params["include[]"] = self.include
        if self.time_zone:
            params["time_zone"] = self.time_zone
        return params


class LogEntries(BaseModel):
    id: str = Field(description="The ID of the log entry")
    summary: str = Field(description="A short summary of the log entry")
    created_at: datetime = Field(description="The time the log entry was created")
    html_url: str | None = Field(
        default=None,
        description="The URL of the log entry in the PagerDuty web UI",
    )
    incident: dict[str, Any] | None = Field(
        default=None,
        description="The incident associated with the log entry",
    )
    teams: list[TeamReference] | None = Field(default=None, description="The teams associated with this schedule")
    service: ServiceReference | None = Field(
        default=None,
        description="The service associated with the alert",
    )
    channel: ChannelReference | None = Field(
        default=None,
        description="The channel body containing details and context",
    )

    @computed_field
    @property
    def type(self) -> Literal["log_entries"]:
        return "log_entries"
