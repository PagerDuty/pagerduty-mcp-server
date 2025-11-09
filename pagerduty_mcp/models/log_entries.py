from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.references import ServiceReference, UserReference

LogEntryType = Literal[
    "trigger_log_entry",
    "acknowledge_log_entry",
    "resolve_log_entry",
    "assign_log_entry",
    "escalate_log_entry",
    "notify_log_entry",
    "reach_trigger_limit_log_entry",
    "repeat_escalation_path_log_entry",
    "exhaust_escalation_path_log_entry",
    "unacknowledge_log_entry",
    "annotate_log_entry",
    "snooze_log_entry",
    "unsnooze_log_entry",
]

TimeZone = Literal["UTC"]


class IncidentReference(BaseModel):
    """Reference to an incident."""

    id: str = Field(description="The ID of the incident")
    type: Literal["incident_reference"] = Field(
        default="incident_reference", description="The type of reference"
    )
    summary: str | None = Field(default=None, description="A short summary of the incident")
    self: str | None = Field(default=None, description="API URL for the incident")
    html_url: str | None = Field(default=None, description="Web URL for the incident")


class ChannelReference(BaseModel):
    """Reference to a notification channel."""

    type: str = Field(description="The type of notification channel (e.g., 'email', 'sms', 'push_notification')")
    summary: str | None = Field(default=None, description="Summary of the channel")


class LogEntry(BaseModel):
    """A log entry representing an action taken on an incident.

    Log entries provide a complete audit trail of all actions on an incident,
    including who performed the action and when. This is especially useful for
    resolved incidents where assignments and acknowledgments are no longer
    available through the regular incident API.
    """

    model_config = ConfigDict(extra="allow")

    id: str = Field(description="The ID of the log entry")
    type: LogEntryType = Field(description="The type of log entry")
    summary: str = Field(description="A short summary of what happened")
    self: str = Field(description="The API URL for this log entry")
    html_url: str | None = Field(default=None, description="The web URL for this log entry")
    created_at: datetime = Field(description="When the log entry was created")
    agent: UserReference | ServiceReference | None = Field(
        default=None,
        description="The agent (user or service) that performed the action. "
        "For resolve_log_entry, this is the user who resolved the incident. "
        "For acknowledge_log_entry, this is the user who acknowledged it.",
    )
    channel: ChannelReference | None = Field(
        default=None, description="The notification channel (for notify_log_entry types)"
    )
    service: ServiceReference | None = Field(default=None, description="The service associated with the log entry")
    incident: IncidentReference = Field(description="The incident this log entry is associated with")
    teams: list[dict[str, Any]] | None = Field(
        default=None, description="Teams associated with the incident at the time of the log entry"
    )
    contexts: list[dict[str, Any]] | None = Field(
        default=None, description="Additional context for the log entry"
    )
    event_details: dict[str, Any] | None = Field(
        default=None, description="Additional event details (structure varies by log entry type)"
    )


class LogEntryQuery(BaseModel):
    """Query parameters for listing log entries."""

    model_config = ConfigDict(extra="forbid")

    since: datetime | None = Field(
        default=None, description="Filter log entries that occurred after this time"
    )
    until: datetime | None = Field(
        default=None, description="Filter log entries that occurred before this time"
    )
    time_zone: TimeZone = Field(
        default="UTC",
        description="Time zone for the time window. Currently only UTC is supported.",
    )
    is_overview: bool = Field(
        default=False,
        description="If true, only log entries of type triggers, acknowledges, and resolves are returned",
    )
    include: list[Literal["incidents", "services", "channels", "teams"]] | None = Field(
        default=None,
        description="Array of additional details to include (incidents, services, channels, teams)",
    )
    limit: int | None = Field(
        ge=1,
        le=MAX_RESULTS,
        default=100,
        description="Maximum number of results to return. The maximum is 1000",
    )

    def to_params(self) -> dict[str, Any]:
        """Convert query model to API parameters."""
        params = {"time_zone": self.time_zone, "is_overview": str(self.is_overview).lower()}

        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.include:
            params["include[]"] = self.include
        if self.limit:
            params["limit"] = self.limit

        return params


class IncidentLogEntryQuery(BaseModel):
    """Query parameters for listing log entries for a specific incident."""

    model_config = ConfigDict(extra="forbid")

    since: datetime | None = Field(
        default=None, description="Filter log entries that occurred after this time"
    )
    until: datetime | None = Field(
        default=None, description="Filter log entries that occurred before this time"
    )
    time_zone: TimeZone = Field(
        default="UTC",
        description="Time zone for the time window. Currently only UTC is supported.",
    )
    is_overview: bool = Field(
        default=False,
        description="If true, only log entries of type triggers, acknowledges, and resolves are returned",
    )
    include: list[Literal["incidents", "services", "channels", "teams"]] | None = Field(
        default=None,
        description="Array of additional details to include (incidents, services, channels, teams)",
    )
    limit: int | None = Field(
        ge=1,
        le=MAX_RESULTS,
        default=100,
        description="Maximum number of results to return. The maximum is 1000",
    )

    def to_params(self) -> dict[str, Any]:
        """Convert query model to API parameters."""
        params = {"time_zone": self.time_zone, "is_overview": str(self.is_overview).lower()}

        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.include:
            params["include[]"] = self.include
        if self.limit:
            params["limit"] = self.limit

        return params
