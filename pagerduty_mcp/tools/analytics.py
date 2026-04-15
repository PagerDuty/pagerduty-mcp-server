from pagerduty_mcp.client import get_client
from pagerduty_mcp.models.analytics import AnalyticsResponderMetrics, GetResponderMetricsRequest
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
