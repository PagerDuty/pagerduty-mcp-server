from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, AlertQuery, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_alerts(incident_id: str, query_model: AlertQuery) -> ListResponseModel[Alert]:
    """List alerts for a specific incident.

    Args:
        incident_id: The ID of the incident to list alerts for
        query_model: Query parameters for filtering alerts

    Returns:
        List of alerts for the specified incident
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/alerts",
        params=params,
        maximum_records=query_model.limit or 100
    )
    alerts = [Alert(**alert) for alert in response]
    return ListResponseModel[Alert](response=alerts)


def get_alert(incident_id: str, alert_id: str) -> Alert:
    """Get a specific alert by ID for a given incident.

    Args:
        incident_id: The ID of the incident the alert belongs to
        alert_id: The ID of the alert to retrieve

    Returns:
        Alert details
    """
    response = get_client().rget(f"/incidents/{incident_id}/alerts/{alert_id}")
    return Alert.model_validate(response)

