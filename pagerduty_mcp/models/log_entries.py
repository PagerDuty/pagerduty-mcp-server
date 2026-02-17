from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.references import ServiceReference


class Agent(BaseModel):
    """Agent that performed the action."""

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    summary: str | None = None
    self_: str | None = Field(None, alias="self")
    html_url: str | None = None


class Channel(BaseModel):
    """Channel through which the action was performed."""

    model_config = ConfigDict(extra="allow")

    type: str | None = None


class Team(BaseModel):
    """Team reference."""

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    summary: str | None = None
    self_: str | None = Field(None, alias="self")
    html_url: str | None = None


class LogEntry(BaseModel):
    """Log entry model representing a PagerDuty log entry.

    Note: Log entries have polymorphic types (AcknowledgeLogEntry, TriggerLogEntry, etc.).
    This base model handles common fields across all log entry types.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    summary: str | None = None
    self_: str = Field(alias="self")
    html_url: str | None = None
    created_at: datetime
    agent: Agent | None = None
    channel: Channel | None = None
    service: ServiceReference | None = None
    incident: dict[str, Any] | None = None  # Incident reference
    teams: list[Team] | None = None


class LogEntryQuery(BaseModel):
    """Query parameters for listing log entries."""

    model_config = ConfigDict(extra="forbid")

    since: datetime | None = Field(
        default=None,
        description="The start of the date range to search",
    )
    until: datetime | None = Field(
        default=None,
        description="The end of the date range to search",
    )
    limit: int | None = Field(
        ge=1,
        le=MAX_RESULTS,
        default=100,
        description="Maximum number of results to return",
    )
    offset: int | None = Field(
        ge=0,
        default=0,
        description="Offset for pagination",
    )
    is_overview: bool | None = Field(
        default=None,
        description="If true, returns only the most important changes to the incident",
    )
    include: list[str] | None = Field(
        default=None,
        description="Array of additional models to include. Options: 'incidents', 'services', 'channels', 'teams'",
    )
    team_ids: list[str] | None = Field(
        default=None,
        description="Filter log entries by team IDs",
    )
    time_zone: str | None = Field(
        default=None,
        description="Time zone for the results (e.g., 'America/New_York', 'UTC')",
    )
    total: bool | None = Field(
        default=None,
        description="Include total count of log entries in the response",
    )

    @field_validator("since", "until", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for datetime fields."""
        if v == "" or v is None:
            return None
        return v

    def to_params(self) -> dict[str, Any]:
        """Convert query model to API parameters."""
        params: dict[str, Any] = {}

        if self.since is not None:
            params["since"] = self.since.isoformat()
        if self.until is not None:
            params["until"] = self.until.isoformat()
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.is_overview is not None:
            params["is_overview"] = self.is_overview
        if self.include:
            params["include[]"] = self.include
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.time_zone is not None:
            params["time_zone"] = self.time_zone
        if self.total is not None:
            params["total"] = self.total

        return params
