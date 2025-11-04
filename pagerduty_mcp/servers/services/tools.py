"""Tools for PagerDuty Services MCP Server."""

from pagerduty_mcp.common import get_client, paginate
from pagerduty_mcp.models import ListResponseModel
from .models import Service, ServiceCreate, ServiceQuery


def list_services(query_model: ServiceQuery) -> ListResponseModel[Service]:
    """List all services.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of services matching the query parameters
    """
    response = paginate(client=get_client(), entity="services", params=query_model.to_params())
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

    Args:
        service_data: The data for the new service.
        Do not include the ID in the data since it is auto-generated.
        Always include the summary field for all references if available.

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


# Tool lists for registration
READ_TOOLS = [
    list_services,
    get_service,
]

WRITE_TOOLS = [
    create_service,
    update_service,
]
