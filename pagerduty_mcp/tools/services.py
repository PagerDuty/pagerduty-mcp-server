from pagerduty_mcp.models import ListResponseModel, Service, ServiceCreate, ServiceQuery, MCPContext
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def list_services(query_model: ServiceQuery, context: MCPContext) -> ListResponseModel[Service]:
    """List all services.

    Args:
        query_model: Optional filtering parameters
        context: The MCP context with client and user info (injected)

    Returns:
        List of services matching the query parameters
    """
    response = paginate(client=context.client, entity="services", params=query_model.to_params())
    services = [Service(**service) for service in response]
    return ListResponseModel[Service](response=services)


@inject_context
def get_service(service_id: str, context: MCPContext) -> Service:
    """Get details for a specific service.

    Args:
        service_id: The ID of the service to retrieve
        context: The MCP context with client and user info (injected)

    Returns:
        The service details
    """
    response = context.client.rget(f"/services/{service_id}")
    return Service.model_validate(response)


@inject_context
def create_service(service_data: ServiceCreate, context: MCPContext) -> Service:
    """Create a new service.

    Args:
        service_data: The data for the new service.
        Do not include the ID in the data since it is auto-generated.
        Always include the summary field for all references if available.
        context: The MCP context with client and user info (injected)

    Returns:
        The created service
    """
    response = context.client.rpost("/services", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"])

    return Service.model_validate(response)


@inject_context
def update_service(service_id: str, service_data: ServiceCreate, context: MCPContext) -> Service:
    """Update an existing service.

    Args:
        service_id: The ID of the service to update
        service_data: The updated service data
        context: The MCP context with client and user info (injected)

    Returns:
        The updated service
    """
    response = context.client.rput(f"/services/{service_id}", json=service_data.model_dump())

    if type(response) is dict and "service" in response:
        return Service.model_validate(response["service"])

    return Service.model_validate(response)
