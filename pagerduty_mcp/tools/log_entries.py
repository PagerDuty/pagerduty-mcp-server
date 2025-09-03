from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, LogEntries, LogEntriesQuery, GetLogEntriesQuery
from pagerduty_mcp.utils import paginate


def list_log_entries(query_model: LogEntriesQuery) -> ListResponseModel[LogEntries]:
    """List log entries for a specific incident.

    Returns:
        List of log entries matching the query parameters
    """
    response = paginate(
        client=get_client(),
        entity="log_entries",
        params=query_model.to_params(),
        maximum_records=query_model.limit or 100,
    )
    log_entries = [LogEntries(**log_entry) for log_entry in response]
    return ListResponseModel[LogEntries](response=log_entries)


def get_log_entry(log_entry_id: str, query_model: GetLogEntriesQuery) -> LogEntries:
    """Get a specific log entry by ID for a given incident.

    Args:
        log_entry_id: The ID of the log entry to retrieve
        query_model: Query parameters to include additional data (like channels)

    Returns:
        Log entry details
    """
    params = query_model.to_params()
    response = get_client().rget(f"/log_entries/{log_entry_id}", params=params)
    return LogEntries.model_validate(response)
