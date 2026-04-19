from pagerduty_mcp.client import get_client
from pagerduty_mcp.models.analytics import (
    AnalyticsResponderMetrics,
    AnalyticsServiceMetrics,
    AnalyticsTeamMetrics,
    AnalyticsResponderLoad,
    GetResponderMetricsRequest,
    GetIncidentMetricsByServiceRequest,
    GetIncidentMetricsByTeamRequest,
    GetResponderLoadMetricsRequest,
)
from pagerduty_mcp.models.base import ListResponseModel


def get_responder_metrics(request: GetResponderMetricsRequest) -> str:
    """Get responder metrics aggregated by team from PagerDuty Analytics.

    Returns per-user oncall seconds, interruption counts (business hours, off hours, sleep hours),
    engaged time, and incident counts for a given date range. Powered by PagerDuty's analytics
    engine — oncall hours are computed authoritatively, accounting for schedule overlaps.

    Args:
        request: Filters (required date range, optional team/responder/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsResponderMetrics objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/responders/teams", json=body)

    # The analytics endpoint returns {"data": [...], "filters": {...}, "time_zone": "..."}
    # The pdpyras client may return the raw dict or unwrap it — handle both.
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []

    metrics = [AnalyticsResponderMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsResponderMetrics](response=metrics).model_dump_json()


def get_incident_metrics_by_service(request: GetIncidentMetricsByServiceRequest) -> str:
    """Get aggregated incident metrics per service from PagerDuty Analytics.

    Returns service-level MTTA, mean MTTR, escalation counts, incident
    volume, and uptime percentage. Use this instead of list_incidents when you need
    service health metrics — data is pre-aggregated by PagerDuty's analytics engine.

    Args:
        request: Filters (required date range, optional team/service/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsServiceMetrics objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/incidents/services", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsServiceMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsServiceMetrics](response=metrics).model_dump_json()


def get_incident_metrics_by_team(request: GetIncidentMetricsByTeamRequest) -> str:
    """Get aggregated incident metrics per team from PagerDuty Analytics.

    Returns team-level MTTA, mean MTTR, escalation counts, incident
    volume, and uptime percentage. Use for team performance comparisons and dashboards.

    Args:
        request: Filters (required date range, optional team/service/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsTeamMetrics objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/incidents/teams", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsTeamMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsTeamMetrics](response=metrics).model_dump_json()


def get_responder_load_metrics(request: GetResponderLoadMetricsRequest) -> str:
    """Get aggregated load metrics per responder from PagerDuty Analytics.

    Returns per-responder on-call hours, incident count, acknowledgment count,
    sleep-hour interruptions, and engaged time. Use for responder workload analysis.

    Args:
        request: Filters (required date range, optional team/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsResponderLoad objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/responders/all", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsResponderLoad(**item) for item in raw_data]
    return ListResponseModel[AnalyticsResponderLoad](response=metrics).model_dump_json()
