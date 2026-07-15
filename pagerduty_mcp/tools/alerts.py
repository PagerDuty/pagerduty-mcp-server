from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, ListResponseModel
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

    Both IDs must be known, non-empty PagerDuty IDs (e.g. "PALERT123").
    If the alert ID is not known, use list_alerts_from_incident to discover
    the incident's alerts instead of calling this tool with an empty or
    placeholder alert_id.

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
