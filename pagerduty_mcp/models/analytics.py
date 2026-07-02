from pydantic import BaseModel, Field


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
    mean_engaged_seconds: int | None = Field(default=None)


class AnalyticsTeamMetrics(BaseModel):
    """Per-team aggregate incident metrics from PagerDuty Analytics."""

    range_start: str | None = Field(default=None, description="ISO8601 start of the aggregation period. Populated when aggregate_unit is set on the request.")
    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    mean_seconds_to_resolve: int | None = Field(default=None, description="Mean MTTR in seconds.")
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None)
    total_business_hour_interruptions: int | None = Field(default=None)
    total_off_hour_interruptions: int | None = Field(default=None)
    total_sleep_hour_interruptions: int | None = Field(default=None)
    mean_engaged_seconds: int | None = Field(default=None)


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
    total_interruptions: int | None = Field(default=None)
    total_business_hour_interruptions: int | None = Field(default=None)
    total_off_hour_interruptions: int | None = Field(default=None)
    mean_engaged_seconds: int | None = Field(default=None)


class AnalyticsAggregatedMetrics(BaseModel):
    """Full-period aggregated incident metrics from PagerDuty Analytics.

    Returned by /analytics/metrics/incidents/all. Only this endpoint
    provides percentile fields (P50-P95).
    """

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None)
    mean_seconds_to_resolve: int | None = Field(default=None)
    p50_seconds_to_first_ack: int | None = Field(default=None)
    p75_seconds_to_first_ack: int | None = Field(default=None)
    p90_seconds_to_first_ack: int | None = Field(default=None)
    p95_seconds_to_first_ack: int | None = Field(default=None)
    p50_seconds_to_resolve: int | None = Field(default=None)
    p75_seconds_to_resolve: int | None = Field(default=None)
    p90_seconds_to_resolve: int | None = Field(default=None)
    p95_seconds_to_resolve: int | None = Field(default=None)
