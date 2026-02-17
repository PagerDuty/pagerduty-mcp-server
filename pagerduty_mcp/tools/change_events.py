from pagerduty_mcp.context import get_client
from pagerduty_mcp.models import ChangeEvent, ChangeEventQuery, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_change_events(query_model: ChangeEventQuery) -> ListResponseModel[ChangeEvent]:
    """List all change events with optional filtering.

    Change Events represent changes to systems, services, and applications that
    can be correlated with incidents to provide context for troubleshooting.

    Args:
        query_model: Query parameters for filtering change events

    Returns:
        List of ChangeEvent objects matching the query parameters
    """
    params = query_model.to_params()
    response = paginate(
        client=get_client(),
        entity="change_events",
        params=params,
        maximum_records=query_model.limit or 100,
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


def list_service_change_events(service_id: str, query_model: ChangeEventQuery) -> ListResponseModel[ChangeEvent]:
    """List all change events for a specific service.

    Args:
        service_id: The ID of the service
        query_model: Query parameters for filtering change events

    Returns:
        List of ChangeEvent objects associated with the service
    """
    params = query_model.to_params()
    response = paginate(
        client=get_client(),
        entity=f"services/{service_id}/change_events",
        params=params,
        maximum_records=query_model.limit or 100,
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
    if limit:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/related_change_events",
        params=params,
        maximum_records=limit or 100,
    )
    change_events = [ChangeEvent(**change_event) for change_event in response]
    return ListResponseModel[ChangeEvent](response=change_events)
