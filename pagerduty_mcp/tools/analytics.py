from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models.analytics import (
    AnalyticsAggregatedMetrics,
    AnalyticsResponderLoad,
    AnalyticsResponderMetrics,
    AnalyticsServiceMetrics,
    AnalyticsTeamMetrics,
)
from pagerduty_mcp.models.base import ListResponseModel


def get_responder_metrics(
    date_range_start: str,
    date_range_end: str,
    team_ids: list[str] | None = None,
    responder_ids: list[str] | None = None,
    urgency: str | None = None,
    time_zone: str | None = None,
    order: str | None = None,
    order_by: str | None = None,
) -> str:
    """Get responder metrics aggregated by team from PagerDuty Analytics.

    Returns per-user oncall seconds, interruption counts (business hours, off hours, sleep hours),
    engaged time, and incident counts for a given date range. Powered by PagerDuty's analytics
    engine — oncall hours are computed authoritatively, accounting for schedule overlaps.

    Args:
        date_range_start: ISO8601 DateTime. Incidents with created_at before this value are omitted.
        date_range_end: ISO8601 DateTime. Incidents with created_at >= this value are omitted.
        team_ids: Only incidents related to these teams will be included.
        responder_ids: Only incidents related to these responders will be included.
        urgency: Filter by urgency: 'high' or 'low'.
        time_zone: The time zone to use for results and grouping (e.g. 'America/New_York').
        order: Sort order: 'asc' or 'desc'.
        order_by: Field to sort results by.

    Returns:
        JSON string of ListResponseModel containing AnalyticsResponderMetrics objects.
    """
    body: dict[str, Any] = {
        "filters": {
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
        }
    }
    if team_ids:
        body["filters"]["team_ids"] = team_ids
    if responder_ids:
        body["filters"]["responder_ids"] = responder_ids
    if urgency:
        body["filters"]["urgency"] = urgency
    if time_zone:
        body["time_zone"] = time_zone
    if order:
        body["order"] = order
    if order_by:
        body["order_by"] = order_by

    response = get_client().rpost("/analytics/metrics/responders/teams", json=body)

    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []

    metrics = [AnalyticsResponderMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsResponderMetrics](response=metrics).model_dump_json()


def get_incident_metrics_by_service(
    created_at_start: str,
    created_at_end: str,
    team_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    urgency: str | None = None,
    time_zone: str | None = None,
    order: str | None = None,
    order_by: str | None = None,
) -> str:
    """Get aggregated incident metrics per service from PagerDuty Analytics.

    Returns service-level MTTA, mean MTTR, escalation counts, incident
    volume, and uptime percentage. Use this instead of list_incidents when you need
    service health metrics — data is pre-aggregated by PagerDuty's analytics engine.

    Args:
        created_at_start: ISO8601 DateTime. Incidents created before this are omitted.
        created_at_end: ISO8601 DateTime. Incidents created on/after this are omitted.
        team_ids: Only incidents related to these teams will be included.
        service_ids: Only incidents related to these services will be included.
        urgency: Filter by urgency: 'high' or 'low'.
        time_zone: The time zone for results (e.g. 'America/New_York').
        order: Sort order: 'asc' or 'desc'.
        order_by: Field to sort results by.

    Returns:
        JSON string of ListResponseModel containing AnalyticsServiceMetrics objects.
    """
    body: dict[str, Any] = {
        "filters": {
            "created_at_start": created_at_start,
            "created_at_end": created_at_end,
        }
    }
    if team_ids:
        body["filters"]["team_ids"] = team_ids
    if service_ids:
        body["filters"]["service_ids"] = service_ids
    if urgency:
        body["filters"]["urgency"] = urgency
    if time_zone:
        body["time_zone"] = time_zone
    if order:
        body["order"] = order
    if order_by:
        body["order_by"] = order_by

    response = get_client().rpost("/analytics/metrics/incidents/services", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsServiceMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsServiceMetrics](response=metrics).model_dump_json()


def get_incident_metrics_by_team(
    created_at_start: str,
    created_at_end: str,
    team_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    urgency: str | None = None,
    time_zone: str | None = None,
    order: str | None = None,
    order_by: str | None = None,
    aggregate_unit: str | None = None,
) -> str:
    """Get aggregated incident metrics per team from PagerDuty Analytics.

    Returns team-level MTTA, mean MTTR, escalation counts, incident
    volume, and uptime percentage. Use for team performance comparisons and dashboards.

    Args:
        created_at_start: ISO8601 DateTime. Incidents created before this are omitted.
        created_at_end: ISO8601 DateTime. Incidents created on/after this are omitted.
        team_ids: Only incidents related to these teams will be included.
        service_ids: Only incidents related to these services will be included.
        urgency: Filter by urgency: 'high' or 'low'.
        time_zone: The time zone for results (e.g. 'America/New_York').
        order: Sort order: 'asc' or 'desc'.
        order_by: Field to sort results by.
        aggregate_unit: Time unit to aggregate metrics by: 'day', 'week', or 'month'.
            If omitted, returns a single all-period row.

    Returns:
        JSON string of ListResponseModel containing AnalyticsTeamMetrics objects.
    """
    body: dict[str, Any] = {
        "filters": {
            "created_at_start": created_at_start,
            "created_at_end": created_at_end,
        }
    }
    if team_ids:
        body["filters"]["team_ids"] = team_ids
    if service_ids:
        body["filters"]["service_ids"] = service_ids
    if urgency:
        body["filters"]["urgency"] = urgency
    if time_zone:
        body["time_zone"] = time_zone
    if order:
        body["order"] = order
    if order_by:
        body["order_by"] = order_by
    if aggregate_unit:
        body["aggregate_unit"] = aggregate_unit

    response = get_client().rpost("/analytics/metrics/incidents/teams", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsTeamMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsTeamMetrics](response=metrics).model_dump_json()


def get_responder_load_metrics(
    date_range_start: str,
    date_range_end: str,
    team_ids: list[str] | None = None,
    urgency: str | None = None,
    time_zone: str | None = None,
    order: str | None = None,
    order_by: str | None = None,
) -> str:
    """Get aggregated load metrics per responder from PagerDuty Analytics.

    Returns per-responder on-call hours, incident count, acknowledgment count,
    sleep-hour interruptions, and engaged time. Use for responder workload analysis.

    Args:
        date_range_start: ISO8601 DateTime. Incidents with created_at before this value are omitted.
        date_range_end: ISO8601 DateTime. Incidents with created_at >= this value are omitted.
        team_ids: Only incidents related to these teams will be included.
        urgency: Filter by urgency: 'high' or 'low'.
        time_zone: The time zone for results (e.g. 'America/New_York').
        order: Sort order: 'asc' or 'desc'.
        order_by: Field to sort results by.

    Returns:
        JSON string of ListResponseModel containing AnalyticsResponderLoad objects.
    """
    body: dict[str, Any] = {
        "filters": {
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
        }
    }
    if team_ids:
        body["filters"]["team_ids"] = team_ids
    if urgency:
        body["filters"]["urgency"] = urgency
    if time_zone:
        body["time_zone"] = time_zone
    if order:
        body["order"] = order
    if order_by:
        body["order_by"] = order_by

    response = get_client().rpost("/analytics/metrics/responders/all", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsResponderLoad(**item) for item in raw_data]
    return ListResponseModel[AnalyticsResponderLoad](response=metrics).model_dump_json()


def get_incident_metrics_all(
    created_at_start: str,
    created_at_end: str,
    team_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    urgency: str | None = None,
    time_zone: str | None = None,
    order: str | None = None,
    order_by: str | None = None,
) -> str:
    """Get full-period aggregated incident metrics from PagerDuty Analytics.

    Returns rollup metrics for the entire requested period including percentile
    distributions (P50, P75, P90, P95) for ack and resolve times. These percentile
    fields are ONLY available from this endpoint — not from the per-team or per-service
    grouped endpoints.

    Args:
        created_at_start: ISO8601 DateTime. Incidents created before this are omitted.
        created_at_end: ISO8601 DateTime. Incidents created on/after this are omitted.
        team_ids: Only incidents related to these teams will be included.
        service_ids: Only incidents related to these services will be included.
        urgency: Filter by urgency: 'high' or 'low'.
        time_zone: The time zone for results (e.g. 'America/New_York').
        order: Sort order: 'asc' or 'desc'.
        order_by: Field to sort results by.

    Returns:
        JSON string of AnalyticsAggregatedMetrics object.
    """
    body: dict[str, Any] = {
        "filters": {
            "created_at_start": created_at_start,
            "created_at_end": created_at_end,
        }
    }
    if team_ids:
        body["filters"]["team_ids"] = team_ids
    if service_ids:
        body["filters"]["service_ids"] = service_ids
    if urgency:
        body["filters"]["urgency"] = urgency
    if time_zone:
        body["time_zone"] = time_zone
    if order:
        body["order"] = order
    if order_by:
        body["order_by"] = order_by

    response = get_client().rpost("/analytics/metrics/incidents/all", json=body)
    if isinstance(response, dict):
        data = response.get("data", [])
        raw_data = data[0] if isinstance(data, list) and data else data if isinstance(data, dict) else {}
    elif isinstance(response, list) and len(response) > 0:
        raw_data = response[0]
    else:
        raw_data = {}
    metrics = AnalyticsAggregatedMetrics(**raw_data) if raw_data else AnalyticsAggregatedMetrics()
    return metrics.model_dump_json()
