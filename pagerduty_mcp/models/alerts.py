from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.references import IncidentReference, IntegrationReference, ServiceReference

AlertStatus = Literal["triggered", "acknowledged", "resolved", "suppressed"]
AlertSeverity = Literal["critical", "error", "warning", "info"]


class AlertBody(BaseModel):
    details: dict[str, Any] | str = Field(description="Detailed alert information and context")
    cef_details: dict[str, Any] | None = Field(default=None, description="CEF (Common Event Format) details")

    @computed_field
    @property
    def type(self) -> Literal["alert_body"]:
        return "alert_body"


class Alert(BaseModel):
    id: str = Field(description="Unique alert identifier")
    summary: str = Field(description="Brief alert description")
    status: AlertStatus = Field(description="Current alert status")
    severity: AlertSeverity = Field(description="Alert severity level")
    alert_key: str | None = Field(default=None, description="Deduplication key")
    created_at: datetime = Field(description="Alert creation timestamp")
    resolved_at: datetime | None = Field(default=None, description="Resolution timestamp")
    suppressed: bool | None = Field(default=None, description="Whether the alert is suppressed")

    # Relationships
    service: ServiceReference = Field(description="Associated service")
    incident: IncidentReference | None = Field(default=None, description="Associated incident")
    integration: IntegrationReference | None = Field(default=None, description="Source integration")
    body: AlertBody | None = Field(default=None, description="Detailed alert information")

    @computed_field
    @property
    def type(self) -> Literal["alert"]:
        return "alert"


