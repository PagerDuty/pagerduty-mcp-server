from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalyticsFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_range_start: str = Field(
        description="ISO8601 DateTime. Incidents with created_at before this value are omitted."
    )
    date_range_end: str = Field(
        description="ISO8601 DateTime. Incidents with created_at >= this value are omitted."
    )
    team_ids: list[str] | None = Field(
        default=None,
        description="Only incidents related to these teams will be included.",
    )
    responder_ids: list[str] | None = Field(
        default=None,
        description="Only incidents related to these responders will be included.",
    )
    urgency: str | None = Field(
        default=None,
        description="Filter by urgency: 'high' or 'low'.",
    )


class GetResponderMetricsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsFilters = Field(
        description="Date range and optional filters to scope the metrics."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone to use for results and grouping (e.g. 'America/New_York').",
    )
    order: str | None = Field(
        default=None,
        description="Sort order: 'asc' or 'desc'.",
    )
    order_by: str | None = Field(
        default=None,
        description="Field to sort results by.",
    )

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "date_range_start": self.filters.date_range_start,
                "date_range_end": self.filters.date_range_end,
            }
        }
        if self.filters.team_ids:
            body["filters"]["team_ids"] = self.filters.team_ids
        if self.filters.responder_ids:
            body["filters"]["responder_ids"] = self.filters.responder_ids
        if self.filters.urgency:
            body["filters"]["urgency"] = self.filters.urgency
        if self.time_zone:
            body["time_zone"] = self.time_zone
        if self.order:
            body["order"] = self.order
        if self.order_by:
            body["order_by"] = self.order_by
        return body


class AnalyticsResponderMetrics(BaseModel):
    """Per-responder aggregate metrics from PagerDuty Analytics."""

    responder_id: str | None = Field(default=None, description="ID of the responder (user).")
    responder_name: str | None = Field(default=None, description="Name of the responder (user).")
    team_id: str | None = Field(default=None, description="ID of the team associated with the responder.")
    team_name: str | None = Field(default=None, description="Name of the team associated with the responder.")

    total_seconds_on_call: int | None = Field(default=None, description="Total seconds the responder was on call.")
    total_seconds_on_call_level_1: int | None = Field(
        default=None, description="Total seconds on call at escalation level 1."
    )
    total_seconds_on_call_level_2_plus: int | None = Field(
        default=None, description="Total seconds on call at escalation level 2 or higher."
    )

    total_incident_count: int | None = Field(default=None, description="Total number of incidents created.")
    total_interruptions: int | None = Field(default=None, description="Total number of unique interruptions.")
    total_business_hour_interruptions: int | None = Field(
        default=None,
        description="Unique interruptions during business hours (8am–6pm Mon–Fri, user's time zone).",
    )
    total_off_hour_interruptions: int | None = Field(
        default=None,
        description="Unique interruptions during off hours (6pm–10pm Mon–Fri and all day Sat–Sun, user's time zone).",
    )
    total_sleep_hour_interruptions: int | None = Field(
        default=None,
        description="Unique interruptions during sleep hours (10pm–8am every day, user's time zone).",
    )

    total_engaged_seconds: int | None = Field(
        default=None,
        description="Total engaged time (from acknowledgment until resolution) across all incidents.",
    )
    mean_engaged_seconds: int | None = Field(
        default=None, description="Mean engaged time across all incidents."
    )
    mean_time_to_acknowledge_seconds: int | None = Field(
        default=None,
        description="Average time between first assignment and first acknowledgment.",
    )

    total_notifications: int | None = Field(
        default=None, description="Total incident notifications sent."
    )
    total_incidents_acknowledged: int | None = Field(
        default=None, description="Total incidents explicitly acknowledged by the user."
    )
    total_incidents_manual_escalated_from: int | None = Field(default=None)
    total_incidents_manual_escalated_to: int | None = Field(default=None)
    total_incidents_reassigned_from: int | None = Field(default=None)
    total_incidents_reassigned_to: int | None = Field(default=None)
    total_incidents_timeout_escalated_from: int | None = Field(default=None)
    total_incidents_timeout_escalated_to: int | None = Field(default=None)


class AnalyticsIncidentFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    created_at_start: str = Field(
        description="ISO8601 DateTime. Incidents created before this are omitted."
    )
    created_at_end: str = Field(
        description="ISO8601 DateTime. Incidents created on/after this are omitted."
    )
    team_ids: list[str] | None = Field(
        default=None,
        description="Only incidents related to these teams will be included.",
    )
    service_ids: list[str] | None = Field(
        default=None,
        description="Only incidents related to these services will be included.",
    )
    urgency: str | None = Field(
        default=None,
        description="Filter by urgency: 'high' or 'low'.",
    )


class GetIncidentMetricsByServiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsIncidentFilters = Field(
        description="Date range and optional filters to scope the metrics."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone for results (e.g. 'America/New_York').",
    )
    order: str | None = Field(default=None, description="Sort order: 'asc' or 'desc'.")
    order_by: str | None = Field(default=None, description="Field to sort results by.")

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "created_at_start": self.filters.created_at_start,
                "created_at_end": self.filters.created_at_end,
            }
        }
        if self.filters.team_ids:
            body["filters"]["team_ids"] = self.filters.team_ids
        if self.filters.service_ids:
            body["filters"]["service_ids"] = self.filters.service_ids
        if self.filters.urgency:
            body["filters"]["urgency"] = self.filters.urgency
        if self.time_zone:
            body["time_zone"] = self.time_zone
        if self.order:
            body["order"] = self.order
        if self.order_by:
            body["order_by"] = self.order_by
        return body


class GetIncidentMetricsByTeamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsIncidentFilters = Field(
        description="Date range and optional filters to scope the metrics."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone for results (e.g. 'America/New_York').",
    )
    order: str | None = Field(default=None, description="Sort order: 'asc' or 'desc'.")
    order_by: str | None = Field(default=None, description="Field to sort results by.")

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "created_at_start": self.filters.created_at_start,
                "created_at_end": self.filters.created_at_end,
            }
        }
        if self.filters.team_ids:
            body["filters"]["team_ids"] = self.filters.team_ids
        if self.filters.service_ids:
            body["filters"]["service_ids"] = self.filters.service_ids
        if self.filters.urgency:
            body["filters"]["urgency"] = self.filters.urgency
        if self.time_zone:
            body["time_zone"] = self.time_zone
        if self.order:
            body["order"] = self.order
        if self.order_by:
            body["order_by"] = self.order_by
        return body


class GetResponderLoadMetricsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsFilters = Field(
        description="Date range (date_range_start/end) and optional filters."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone for results (e.g. 'America/New_York').",
    )
    order: str | None = Field(default=None, description="Sort order: 'asc' or 'desc'.")
    order_by: str | None = Field(default=None, description="Field to sort results by.")

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "date_range_start": self.filters.date_range_start,
                "date_range_end": self.filters.date_range_end,
            }
        }
        if self.filters.team_ids:
            body["filters"]["team_ids"] = self.filters.team_ids
        if self.filters.urgency:
            body["filters"]["urgency"] = self.filters.urgency
        if self.time_zone:
            body["time_zone"] = self.time_zone
        if self.order:
            body["order"] = self.order
        if self.order_by:
            body["order_by"] = self.order_by
        return body


class AnalyticsServiceMetrics(BaseModel):
    """Per-service aggregate incident metrics from PagerDuty Analytics."""

    service_id: str | None = Field(default=None)
    service_name: str | None = Field(default=None)
    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    mean_seconds_to_resolve: int | None = Field(default=None, description="Mean MTTR in seconds.")
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None, description="Service availability percentage.")


class AnalyticsTeamMetrics(BaseModel):
    """Per-team aggregate incident metrics from PagerDuty Analytics."""

    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    mean_seconds_to_resolve: int | None = Field(default=None, description="Mean MTTR in seconds.")
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None)


class AnalyticsResponderLoad(BaseModel):
    """Per-responder aggregate load metrics from PagerDuty Analytics."""

    responder_id: str | None = Field(default=None)
    responder_name: str | None = Field(default=None)
    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_seconds_on_call: int | None = Field(default=None)
    total_incident_count: int | None = Field(default=None)
    total_incidents_acknowledged: int | None = Field(default=None)
    total_sleep_hour_interruptions: int | None = Field(default=None)
    total_engaged_seconds: int | None = Field(default=None)
    mean_time_to_acknowledge_seconds: int | None = Field(default=None)
