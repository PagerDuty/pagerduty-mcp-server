from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.references import ServiceReference

AlertStatus = Literal["triggered", "resolved"]
AlertSeverity = Literal["info", "warning", "error", "critical"]


class AlertQuery(BaseModel):
    status: list[AlertStatus] | None = Field(description="Filter alerts by status", default=None)
    severity: list[AlertSeverity] | None = Field(description="Filter alerts by severity", default=None)
    since: datetime | None = Field(description="Filter alerts since a specific date", default=None)
    until: datetime | None = Field(description="Filter alerts until a specific date", default=None)
    service_ids: list[str] | None = Field(description="Filter alerts by service IDs", default=None)
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
                "resolved_at:asc",
                "resolved_at:desc",
            ]
        ]
        | None
    ) = Field(
        default=None,
        description="Sort field and direction (created_at/resolved_at with asc/desc)",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.status:
            params["statuses[]"] = self.status
        if self.severity:
            params["severities[]"] = self.severity
        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.service_ids:
            params["service_ids[]"] = self.service_ids
        if self.sort_by:
            params["sort_by"] = ",".join(self.sort_by)
        return params


class Alert(BaseModel):
    id: str = Field(description="The ID of the alert")
    summary: str = Field(description="A short summary of the alert")
    status: AlertStatus = Field(description="The current status of the alert")
    severity: AlertSeverity = Field(description="The severity of the alert")
    created_at: datetime = Field(description="The time the alert was created")
    resolved_at: datetime | None = Field(
        default=None,
        description="The time the alert was resolved or null if not resolved",
    )
    service: ServiceReference | None = Field(
        default=None,
        description="The service associated with the alert",
    )
    html_url: str | None = Field(
        default=None,
        description="The URL of the alert in the PagerDuty web UI",
    )
    incident: dict[str, Any] | None = Field(
        default=None,
        description="The incident associated with the alert",
    )
    body: dict[str, Any] | None = Field(
        default=None,
        description="The alert body containing details and context",
    )
    first_trigger_log_entry: dict[str, Any] | None = Field(
        default=None,
        description="The first log entry for the alert",
    )

    @computed_field
    @property
    def type(self) -> Literal["alert"]:
        return "alert"
