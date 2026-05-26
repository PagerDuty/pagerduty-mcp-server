from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, ListResponseModel
from pagerduty_mcp.utils import paginate


def get_alert_from_incident(incident_id: str, alert_id: str) -> Alert:
    """Get a specific alert from an incident.

    Args:
        incident_id: The ID of the incident
        alert_id: The ID of the alert

    Returns:
        Alert details
    """
    response = get_client().rget(f"/incidents/{incident_id}/alerts/{alert_id}")
    return Alert.model_validate(response)


def list_alerts_from_incident(
    incident_id: str,
    limit: int | None = 100,
    offset: int | None = 0,
) -> ListResponseModel[Alert]:
    """List alerts for a specific incident.

    Args:
        incident_id: The ID of the incident
        limit: Maximum number of results to return (1-1000). Default is 100.
        offset: Offset for pagination. Default is 0.

    Returns:
        List of Alert objects for the given incident
    """
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/alerts",
        params=params,
        maximum_records=limit or 100,
    )
    alerts = [Alert(**alert) for alert in response]
    return ListResponseModel[Alert](response=alerts)
