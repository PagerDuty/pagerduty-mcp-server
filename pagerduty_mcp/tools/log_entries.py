from datetime import datetime, timedelta, timezone

from pagerduty_mcp.models import ListResponseModel, LogEntry, LogEntryQuery, MCPContext
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def get_log_entry(log_entry_id: str, context: MCPContext) -> LogEntry:
    """Get a specific log entry by ID.

    Args:
        log_entry_id: The ID of the log entry
        context: The MCP context with client and user info (injected)

    Returns:
        LogEntry details
    """
    response = context.client.rget(f"/log_entries/{log_entry_id}")
    return LogEntry.model_validate(response)


@inject_context
def list_log_entries(query_model: LogEntryQuery, context: MCPContext) -> ListResponseModel[LogEntry]:
    """List all log entries across the account.

    Log entries are records of all events on your account. This function allows you
    to filter log entries by time range and paginate through results.

    If no time range is specified, defaults to the last 7 days.

    Args:
        query_model: Query parameters including since, until, limit, and offset
        context: The MCP context with client and user info (injected)

    Returns:
        List of LogEntry objects matching the query parameters

    """
    # Default to last 7 days if no time range specified
    if query_model.since is None:
        query_model.since = datetime.now(timezone.utc) - timedelta(days=7)
    if query_model.until is None:
        query_model.until = datetime.now(timezone.utc)

    params = query_model.to_params()

    response = paginate(
        client=context.client,
        entity="log_entries",
        params=params,
        maximum_records=query_model.limit or 100,
    )
    log_entries = [LogEntry(**entry) for entry in response]
    return ListResponseModel[LogEntry](response=log_entries)
