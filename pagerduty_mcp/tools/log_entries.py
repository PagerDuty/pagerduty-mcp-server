from datetime import UTC, datetime, timedelta
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, LogEntry
from pagerduty_mcp.utils import paginate


def get_log_entry(log_entry_id: str) -> LogEntry:
    """Get a specific log entry by ID.

    Args:
        log_entry_id: The ID of the log entry

    Returns:
        LogEntry details
    """
    response = get_client().rget(f"/log_entries/{log_entry_id}")
    return LogEntry.model_validate(response)


def list_log_entries(
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = 100,
    offset: int | None = 0,
    is_overview: bool | None = None,
    include: list[str] | None = None,
    team_ids: list[str] | None = None,
    time_zone: str | None = None,
    total: bool | None = None,
) -> ListResponseModel[LogEntry]:
    """List all log entries across the account.

    Log entries are records of all events on your account. This function allows you
    to filter log entries by time range and paginate through results.

    If no time range is specified, defaults to the last 7 days.

    Args:
        since: The start of the date range to search. Defaults to 7 days ago.
        until: The end of the date range to search. Defaults to now.
        limit: Maximum number of results to return. Default 100.
        offset: Offset for pagination. Default 0.
        is_overview: If True, returns only the most important changes to the incident.
        include: Array of additional models to include. Options: 'incidents', 'services', 'channels', 'teams'.
        team_ids: Filter log entries by team IDs.
        time_zone: Time zone for the results (e.g., 'America/New_York', 'UTC').
        total: Include total count of log entries in the response.

    Returns:
        List of LogEntry objects matching the query parameters
    """
    if since is None:
        since = datetime.now(UTC) - timedelta(days=7)
    if until is None:
        until = datetime.now(UTC)

    params: dict[str, Any] = {
        "since": since.isoformat(),
        "until": until.isoformat(),
    }
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if is_overview is not None:
        params["is_overview"] = is_overview
    if include:
        params["include[]"] = include
    if team_ids:
        params["team_ids[]"] = team_ids
    if time_zone is not None:
        params["time_zone"] = time_zone
    if total is not None:
        params["total"] = total

    response = paginate(
        client=get_client(),
        entity="log_entries",
        params=params,
        maximum_records=limit or 100,
    )
    log_entries = [LogEntry(**entry) for entry in response]
    return ListResponseModel[LogEntry](response=log_entries)


def list_incident_log_entries(incident_id: str, limit: int | None = None) -> str:
    """List all log entries for a specific incident.

    Log entries for an incident record every state change and action: trigger, acknowledge,
    reassign, escalate, annotate (note), and resolve events.

    Args:
        incident_id: The ID of the incident to retrieve log entries for
        limit: Maximum number of results to return (optional, defaults to 100)

    Returns:
        JSON string of ListResponseModel containing LogEntry objects
    """
    params: dict = {"is_overview": "false"}
    if limit is not None:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/log_entries",
        params=params,
        maximum_records=limit or 100,
    )
    log_entries = [LogEntry(**entry) for entry in response]
    return ListResponseModel[LogEntry](response=log_entries).model_dump_json()
