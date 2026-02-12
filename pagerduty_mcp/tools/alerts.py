from pagerduty_mcp.models import Alert, AlertQuery, ListResponseModel, MCPContext
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def get_alert_from_incident(incident_id: str, alert_id: str, context: MCPContext) -> Alert:
    """Get a specific alert from an incident.

    Args:
        incident_id: The ID of the incident
        alert_id: The ID of the alert
        context: The MCP context with client and user info (injected)

    Returns:
        Alert details
    """
    response = context.client.rget(f"/incidents/{incident_id}/alerts/{alert_id}")
    return Alert.model_validate(response)


@inject_context
def list_alerts_from_incident(incident_id: str, query_model: AlertQuery, context: MCPContext) -> ListResponseModel[Alert]:
    """List alerts for a specific incident.

    Args:
        incident_id: The ID of the incident
        query_model: Query parameters for pagination
        context: The MCP context with client and user info (injected)

    Returns:
        List of Alert objects for the incident

    """
    params = query_model.to_params()

    response = paginate(
        client=context.client,
        entity=f"incidents/{incident_id}/alerts",
        params=params,
        maximum_records=query_model.limit or 100,
    )
    alerts = [Alert(**alert) for alert in response]
    return ListResponseModel[Alert](response=alerts)
