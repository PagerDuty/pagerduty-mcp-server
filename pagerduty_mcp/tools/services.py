from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, Service, ServiceCreate, ServiceQuery
from pagerduty_mcp.utils import paginate


def list_services(query_model: ServiceQuery) -> str:
    """List all services.

    Args:
        query_model: Optional filtering parameters

    Returns:
        JSON string of ListResponseModel containing Service objects
    """
    response = paginate(client=get_client(), entity="services", params=query_model.to_params())
    services = [Service(**service) for service in response]
    return ListResponseModel[Service](response=services).model_dump_json()


def get_service(service_id: str) -> str:
    """Get details for a specific service.

    Args:
        service_id: The ID of the service to retrieve

    Returns:
        JSON string of the service details
    """
    response = get_client().rget(f"/services/{service_id}")
    return Service.model_validate(response).model_dump_json()


# TODO: Add deterministic check for summary field
def create_service(service_data: ServiceCreate) -> str:
    """Create a new service.

    Args:
        service_data: The data for the new service.
        Do not include the ID in the data since it is auto-generated.
        Always include the summary field for all references if available.

    Returns:
        JSON string of the created service
    """
    response = get_client().rpost("/services", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"]).model_dump_json()

    return Service.model_validate(response).model_dump_json()


def update_service(service_id: str, service_data: ServiceCreate) -> str:
    """Update an existing service.

    Args:
        service_id: The ID of the service to update
        service_data: The updated service data

    Returns:
        JSON string of the updated service
    """
    response = get_client().rput(f"/services/{service_id}", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"]).model_dump_json()

    return Service.model_validate(response).model_dump_json()
