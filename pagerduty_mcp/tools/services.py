import json
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, Service, ServiceCreate
from pagerduty_mcp.utils import paginate


def list_services(
    query: str | None = None,
    teams_ids: list[str] | None = None,
    limit: int | None = None,
) -> ListResponseModel[Service]:
    """List all services.

    Args:
        query: Filter by name
        teams_ids: Filter by team IDs
        limit: Max results to return

    Returns:
        List of services matching the query parameters
    """
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    if teams_ids:
        params["team_ids[]"] = teams_ids
    if limit:
        params["limit"] = limit
    response = paginate(client=get_client(), entity="services", params=params, maximum_records=limit or 1000)
    services = [Service(**service) for service in response]
    return ListResponseModel[Service](response=services)


def get_service(service_id: str) -> Service:
    """Get details for a specific service.

    Args:
        service_id: The ID of the service to retrieve

    Returns:
        The service details
    """
    response = get_client().rget(f"/services/{service_id}")
    return Service.model_validate(response)


# TODO: Add deterministic check for summary field
def create_service(service_data: ServiceCreate) -> Service:
    """Create a new service.

    The escalation_policy reference only requires the 'id' field. The 'summary'
    field is server-generated and ignored for object references.

    Example escalation_policy: {"id": "PXXXXXX"}

    Args:
        service_data: The data for the new service.
        Do not include the ID in the data since it is auto-generated.

    Returns:
        The created service
    """
    response = get_client().rpost("/services", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"])

    return Service.model_validate(response)


def update_service(service_id: str, service_data: ServiceCreate) -> Service:
    """Update an existing service.

    Args:
        service_id: The ID of the service to update
        service_data: The updated service data

    Returns:
        The updated service
    """
    response = get_client().rput(f"/services/{service_id}", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"])

    return Service.model_validate(response)


def get_technical_service_dependencies(service_id: str) -> str:
    """Get dependencies for a technical service.

    Args:
        service_id: The ID of the technical service

    Returns:
        JSON string with relationships list
    """
    client = get_client()
    resp = client.get(f"/service_dependencies/technical_services/{service_id}")
    resp.raise_for_status()
    data = resp.json()
    return json.dumps({"relationships": data.get("relationships", [])})
