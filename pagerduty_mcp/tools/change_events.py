from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ChangeEvent, ChangeEventQuery, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_change_events(query_model: ChangeEventQuery) -> str:
    """List all change events with optional filtering.

    Change Events represent changes to systems, services, and applications that
    can be correlated with incidents to provide context for troubleshooting.

    Args:
        query_model: Query parameters for filtering change events

    Returns:
        JSON string of ListResponseModel containing ChangeEvent objects
    """
    params = query_model.to_params()
    response = paginate(
        client=get_client(),
        entity="change_events",
        params=params,
        maximum_records=query_model.limit or 100,
    )
    change_events = [ChangeEvent(**change_event) for change_event in response]
    return ListResponseModel[ChangeEvent](response=change_events).model_dump_json()


def get_change_event(change_event_id: str) -> str:
    """Get details about a specific change event.

    Args:
        change_event_id: The ID of the change event to retrieve

    Returns:
        JSON string of ChangeEvent details
    """
    response = get_client().rget(f"/change_events/{change_event_id}")

    # Handle wrapped response
    if isinstance(response, dict) and "change_event" in response:
        return ChangeEvent.model_validate(response["change_event"]).model_dump_json()

    return ChangeEvent.model_validate(response).model_dump_json()


def list_service_change_events(service_id: str, query_model: ChangeEventQuery) -> str:
    """List all change events for a specific service.

    Args:
        service_id: The ID of the service
        query_model: Query parameters for filtering change events

    Returns:
        JSON string of ListResponseModel containing ChangeEvent objects
    """
    params = query_model.to_params()
    response = paginate(
        client=get_client(),
        entity=f"services/{service_id}/change_events",
        params=params,
        maximum_records=query_model.limit or 100,
    )
    change_events = [ChangeEvent(**change_event) for change_event in response]
    return ListResponseModel[ChangeEvent](response=change_events).model_dump_json()


def list_incident_change_events(incident_id: str, limit: int | None = None) -> str:
    """List change events related to a specific incident.

    Args:
        incident_id: The ID of the incident
        limit: Maximum number of results to return (optional)

    Returns:
        JSON string of ListResponseModel containing ChangeEvent objects
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
    return ListResponseModel[ChangeEvent](response=change_events).model_dump_json()
