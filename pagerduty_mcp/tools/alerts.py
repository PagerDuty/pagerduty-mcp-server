from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, ListResponseModel


def list_incident_alerts(incident_id: str) -> ListResponseModel[Alert]:
    """List alerts associated with a specific incident.

    Args:
        incident_id: The ID of the incident to retrieve alerts for

    Returns:
        List of Alert objects associated with the incident

    Examples:
        Basic usage for retrieving alerts for an incident:

        >>> alerts = list_incident_alerts("PHJKLMN")
        >>> isinstance(alerts.response, list)
        True
    """
    response = get_client().rget(f"/incidents/{incident_id}/alerts")
    alert_data = response.get("alerts", []) if isinstance(response, dict) else response
    alerts = [Alert(**alert) for alert in alert_data]
    return ListResponseModel[Alert](response=alerts)