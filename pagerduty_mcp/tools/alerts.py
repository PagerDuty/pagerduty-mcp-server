from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, AlertQuery, ListResponseModel
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


def list_alerts_from_incident(incident_id: str, query_model: AlertQuery) -> ListResponseModel[Alert]:
    """List alerts for a specific incident.

    Args:
        incident_id: The ID of the incident
        query_model: Query parameters for pagination

    Returns:
        List of Alert objects for the incident

    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/alerts",
        params=params,
        maximum_records=query_model.limit or 100,
    )
    alerts = [Alert(**alert) for alert in response]
    return ListResponseModel[Alert](response=alerts)
