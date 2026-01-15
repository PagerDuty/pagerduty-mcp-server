from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.references import ServiceReference


class IncidentReference(BaseModel):
    """Reference to an incident."""

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    summary: str | None = None
    self_: str | None = Field(None, alias="self")
    html_url: str | None = None


class IntegrationReference(BaseModel):
    """Reference to an integration."""

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    summary: str | None = None
    self_: str | None = Field(None, alias="self")
    html_url: str | None = None


class AlertBody(BaseModel):
    """Alert body with details and contexts."""

    model_config = ConfigDict(extra="allow")

    type: str | None = None
    contexts: list[dict[str, Any]] | None = None
    details: dict[str, Any] | None = None


class Alert(BaseModel):
    """Alert model representing a PagerDuty alert."""

    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    summary: str
    self_: str = Field(alias="self")
    html_url: str
    created_at: datetime
    status: str
    alert_key: str
    service: ServiceReference | None = None
    incident: IncidentReference | None = None
    body: AlertBody | None = None
    severity: str | None = None
    suppressed: bool | None = None
    integration: IntegrationReference | None = None


class AlertQuery(BaseModel):
    """Query parameters for listing alerts."""

    model_config = ConfigDict(extra="forbid")

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

    def to_params(self) -> dict[str, Any]:
        """Convert query model to API parameters."""
        params: dict[str, Any] = {}

        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset

        return params
