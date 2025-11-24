from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ChangeEvent, ChangeEventQuery, ChangeEventUpdateRequest, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_change_events(query_model: ChangeEventQuery) -> ListResponseModel[ChangeEvent]:
    """List all change events with optional filtering.

    Change Events represent changes to systems, services, and applications that
    can be correlated with incidents to provide context for troubleshooting.

    Args:
        query_model: Optional filtering parameters including:
            - limit: Maximum number of results to return
            - offset: Offset for pagination
            - total: Whether to include total count
            - team_ids: Filter by team IDs
            - integration_ids: Filter by integration IDs
            - since: Filter by start date
            - until: Filter by end date

    Returns:
        List of ChangeEvent objects matching the query parameters

    Examples:
        List recent change events:

        >>> from pagerduty_mcp.models import ChangeEventQuery
        >>> from datetime import datetime, timedelta
        >>> since = datetime.now() - timedelta(days=7)
        >>> result = list_change_events(ChangeEventQuery(since=since, limit=25))
        >>> isinstance(result.response, list)
        True

        Filter by specific teams:

        >>> result = list_change_events(ChangeEventQuery(team_ids=["TEAM123"], limit=50))
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
        ChangeEvent details including summary, timestamp, services, integration,
        and custom details

    Examples:
        Get a specific change event:

        >>> change_event = get_change_event("CHE123ABC")
        >>> change_event.id
        'CHE123ABC'
    """
    response = get_client().rget(f"/change_events/{change_event_id}")

    # Handle wrapped response
    if isinstance(response, dict) and "change_event" in response:
        return ChangeEvent.model_validate(response["change_event"])

    return ChangeEvent.model_validate(response)


def list_service_change_events(service_id: str, query_model: ChangeEventQuery) -> ListResponseModel[ChangeEvent]:
    """List all change events for a specific service.

    This retrieves all change events associated with a particular service,
    which can help identify changes that may have impacted service availability.

    Args:
        service_id: The ID of the service
        query_model: Optional filtering parameters including:
            - since: Filter by start date
            - until: Filter by end date
            - limit: Maximum number of results
            - offset: Offset for pagination
            - total: Whether to include total count

    Returns:
        List of ChangeEvent objects associated with the service

    Examples:
        List recent change events for a service:

        >>> from pagerduty_mcp.models import ChangeEventQuery
        >>> from datetime import datetime, timedelta
        >>> since = datetime.now() - timedelta(hours=24)
        >>> result = list_service_change_events(
        ...     "SERV123",
        ...     ChangeEventQuery(since=since, limit=20)
        ... )
        >>> isinstance(result.response, list)
        True
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

    This retrieves change events that are correlated with an incident,
    which can provide context about what changed before or during the incident.
    The correlation is automatically determined by PagerDuty based on timing
    and service relationships.

    Args:
        incident_id: The ID of the incident
        limit: Maximum number of results to return (optional)

    Returns:
        List of ChangeEvent objects related to the incident, including
        correlation metadata that explains why they are related

    Examples:
        List change events related to an incident:

        >>> result = list_incident_change_events("INC123", limit=10)
        >>> isinstance(result.response, list)
        True

        Review changes that may have caused an incident:

        >>> changes = list_incident_change_events("INC456")
        >>> for change in changes.response:
        ...     print(f"{change.timestamp}: {change.summary}")
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


def update_change_event(change_event_id: str, update_data: ChangeEventUpdateRequest) -> ChangeEvent:
    """Update an existing change event.

    Only the summary and custom_details fields can be updated. All other fields
    are read-only and determined when the change event is created.

    Args:
        change_event_id: The ID of the change event to update
        update_data: The updated change event data (summary and/or custom_details)

    Returns:
        The updated ChangeEvent

    Examples:
        Update a change event's summary:

        >>> from pagerduty_mcp.models import ChangeEventUpdateRequest, ChangeEventUpdate
        >>> update = ChangeEventUpdateRequest(
        ...     change_event=ChangeEventUpdate(
        ...         summary="Updated: Deployment completed successfully"
        ...     )
        ... )
        >>> updated = update_change_event("CHE123ABC", update)
        >>> updated.summary
        'Updated: Deployment completed successfully'

        Update custom details:

        >>> update = ChangeEventUpdateRequest(
        ...     change_event=ChangeEventUpdate(
        ...         custom_details={"version": "2.1.0", "deployment_time": "5m"}
        ...     )
        ... )
        >>> updated = update_change_event("CHE123ABC", update)
    """
    response = get_client().rput(
        f"/change_events/{change_event_id}",
        json=update_data.model_dump(exclude_none=True),
    )

    # Handle wrapped response
    if isinstance(response, dict) and "change_event" in response:
        return ChangeEvent.model_validate(response["change_event"])

    return ChangeEvent.model_validate(response)
