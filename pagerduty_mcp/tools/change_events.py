from datetime import datetime
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ChangeEvent, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_change_events(
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = 100,
    offset: int | None = None,
    total: bool | None = None,
    team_ids: list[str] | None = None,
    integration_ids: list[str] | None = None,
) -> ListResponseModel[ChangeEvent]:
    """List all change events with optional filtering.

    Change Events represent changes to systems, services, and applications that
    can be correlated with incidents to provide context for troubleshooting.

    Args:
        since: The start of the date range over which you want to search.
        until: The end of the date range over which you want to search.
        limit: The number of results per page. Default 100.
        offset: The offset of the first record returned.
        total: Set to True to include total count in response.
        team_ids: An array of team IDs. Only results related to these teams will be returned.
        integration_ids: An array of integration IDs. Only results related to these integrations will be returned.

    Returns:
        List of ChangeEvent objects matching the query parameters
    """
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if total is not None:
        params["total"] = total
    if team_ids:
        params["team_ids[]"] = team_ids
    if integration_ids:
        params["integration_ids[]"] = integration_ids
    if since:
        params["since"] = since.isoformat()
    if until:
        params["until"] = until.isoformat()

    response = paginate(
        client=get_client(),
        entity="change_events",
        params=params,
        maximum_records=limit or 100,
    )
    change_events = [ChangeEvent(**change_event) for change_event in response]
    return ListResponseModel[ChangeEvent](response=change_events)


def get_change_event(change_event_id: str) -> ChangeEvent:
    """Get details about a specific change event.

    Args:
        change_event_id: The ID of the change event to retrieve

    Returns:
        ChangeEvent details
    """
    response = get_client().rget(f"/change_events/{change_event_id}")

    # Handle wrapped response
    if isinstance(response, dict) and "change_event" in response:
        return ChangeEvent.model_validate(response["change_event"])

    return ChangeEvent.model_validate(response)


def list_service_change_events(
    service_id: str,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = 100,
    offset: int | None = None,
    total: bool | None = None,
    team_ids: list[str] | None = None,
    integration_ids: list[str] | None = None,
) -> ListResponseModel[ChangeEvent]:
    """List all change events for a specific service.

    Args:
        service_id: The ID of the service.
        since: The start of the date range over which you want to search.
        until: The end of the date range over which you want to search.
        limit: The number of results per page. Default 100.
        offset: The offset of the first record returned.
        total: Set to True to include total count in response.
        team_ids: An array of team IDs. Only results related to these teams will be returned.
        integration_ids: An array of integration IDs. Only results related to these integrations will be returned.

    Returns:
        List of ChangeEvent objects associated with the service
    """
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if total is not None:
        params["total"] = total
    if team_ids:
        params["team_ids[]"] = team_ids
    if integration_ids:
        params["integration_ids[]"] = integration_ids
    if since:
        params["since"] = since.isoformat()
    if until:
        params["until"] = until.isoformat()

    response = paginate(
        client=get_client(),
        entity=f"services/{service_id}/change_events",
        params=params,
        maximum_records=limit or 100,
    )
    change_events = [ChangeEvent(**change_event) for change_event in response]
    return ListResponseModel[ChangeEvent](response=change_events)


def list_incident_change_events(incident_id: str, limit: int | None = None) -> ListResponseModel[ChangeEvent]:
    """List change events related to a specific incident.

    Args:
        incident_id: The ID of the incident
        limit: Maximum number of results to return (optional)

    Returns:
        List of ChangeEvent objects related to the incident
    """
    params = {}
    if limit is not None:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/related_change_events",
        params=params,
        maximum_records=limit or 100,
    )
    change_events = [ChangeEvent(**change_event) for change_event in response]
    return ListResponseModel[ChangeEvent](response=change_events)
