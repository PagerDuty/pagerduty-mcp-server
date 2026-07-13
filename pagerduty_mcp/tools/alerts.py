from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, AlertQuery, ListResponseModel
from pagerduty_mcp.utils import paginate

# Quote marks (straight, curly, backtick), backslashes, and invisible unicode
# (zero-width space/non-joiner/joiner, word joiner, BOM) that clients sometimes
# wrap around or substitute for an empty value.
_ARTIFACT_CHARS = "\"'`\\\u201c\u201d\u2018\u2019\u200b\u200c\u200d\u2060\ufeff"

# Literals that LLM-driven clients serialize in place of a missing value;
# none of these can ever be a valid PagerDuty ID.
_NULL_LITERALS = {"null", "none", "undefined", "nil"}


def _is_blank_id(value: str) -> bool:
    """Return True if the value is empty or a client artifact standing in for empty."""
    if not value:
        return True
    cleaned = value.strip().strip(_ARTIFACT_CHARS).strip()
    return not cleaned or cleaned.lower() in _NULL_LITERALS


def get_alert_from_incident(incident_id: str, alert_id: str) -> Alert:
    """Get a specific alert from an incident.

    Args:
        incident_id: The ID of the incident
        alert_id: The ID of the alert

    Returns:
        Alert details
    """
    if _is_blank_id(incident_id):
        raise ValueError("incident_id must be a non-empty string")
    if _is_blank_id(alert_id):
        raise ValueError(
            "alert_id must be a non-empty string. "
            "To list all alerts for an incident, use list_alerts_from_incident instead."
        )
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
