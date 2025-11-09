from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    IncidentLogEntryQuery,
    ListResponseModel,
    LogEntry,
    LogEntryQuery,
)
from pagerduty_mcp.utils import paginate


def list_log_entries(query_model: LogEntryQuery) -> ListResponseModel[LogEntry]:
    """List log entries across all incidents with optional filtering.

    Log entries provide a complete audit trail of all actions taken on incidents,
    including who performed each action and when. This is particularly useful for
    tracking who resolved or acknowledged incidents after they've been resolved,
    as the PagerDuty API clears assignment lists for resolved incidents.

    Args:
        query_model: Query parameters for filtering log entries

    Returns:
        List of LogEntry objects matching the query parameters

    Examples:
        Get overview of recent incident actions (triggers, acknowledges, resolves):

        >>> from pagerduty_mcp.models import LogEntryQuery
        >>> result = list_log_entries(LogEntryQuery(is_overview=True, limit=50))

        Find all log entries within a time range:

        >>> from datetime import datetime, timedelta
        >>> since = datetime.now() - timedelta(days=7)
        >>> result = list_log_entries(LogEntryQuery(since=since))

        Get detailed log entries with incident and service information:

        >>> result = list_log_entries(LogEntryQuery(include=["incidents", "services"], limit=100))
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity="log_entries",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    log_entries = [LogEntry(**entry) for entry in response]
    return ListResponseModel[LogEntry](response=log_entries)


def list_incident_log_entries(
    incident_id: str, query_model: IncidentLogEntryQuery
) -> ListResponseModel[LogEntry]:
    """List all log entries for a specific incident.

    This is the recommended way to track who handled an incident, especially for
    resolved incidents. The log entries provide a complete audit trail including:
    - Who resolved the incident (resolve_log_entry)
    - Who acknowledged the incident (acknowledge_log_entry)
    - Who was assigned to the incident (assign_log_entry)
    - All other actions taken on the incident

    Unlike the assignments field on incidents (which is cleared when an incident
    is resolved), log entries persist and provide the full historical record.

    Args:
        incident_id: The ID of the incident to get log entries for
        query_model: Query parameters for filtering log entries

    Returns:
        List of LogEntry objects for the specified incident

    Examples:
        Get all log entries for an incident:

        >>> from pagerduty_mcp.models import IncidentLogEntryQuery
        >>> result = list_incident_log_entries("INCIDENT_ID", IncidentLogEntryQuery())

        Get overview of key actions (triggers, acknowledges, resolves):

        >>> result = list_incident_log_entries(
        ...     "INCIDENT_ID",
        ...     IncidentLogEntryQuery(is_overview=True)
        ... )

        Get log entries with full incident details:

        >>> result = list_incident_log_entries(
        ...     "INCIDENT_ID",
        ...     IncidentLogEntryQuery(include=["incidents", "services"])
        ... )

    Note:
        To find who resolved an incident, look for log entries with type="resolve_log_entry"
        and check the "agent" field which contains the user who performed the action.
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/log_entries",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    log_entries = [LogEntry(**entry) for entry in response]
    return ListResponseModel[LogEntry](response=log_entries)


def get_log_entry(log_entry_id: str) -> LogEntry:
    """Get a specific log entry by its ID.

    Args:
        log_entry_id: The ID of the log entry to retrieve

    Returns:
        The log entry details

    Example:
        >>> log_entry = get_log_entry("LOG_ENTRY_ID")
        >>> print(f"Action: {log_entry.type}, User: {log_entry.agent.summary}")
    """
    response = get_client().rget(f"/log_entries/{log_entry_id}")
    return LogEntry.model_validate(response)
