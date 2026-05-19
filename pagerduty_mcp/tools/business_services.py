from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.base import Relationship
from pagerduty_mcp.models.business_services import (
    BusinessService,
    BusinessServiceDependencyList,
    BusinessServiceQuery,
)
from pagerduty_mcp.utils import paginate


def list_business_services(query_model: BusinessServiceQuery) -> ListResponseModel[BusinessService]:
    """List business services.

    Args:
        query_model: Optional filtering parameters

    Returns:
        ListResponseModel containing BusinessService objects
    """
    response = paginate(client=get_client(), entity="business_services", params=query_model.to_params())
    services = [BusinessService(**service) for service in response]
    return ListResponseModel[BusinessService](response=services)


def get_business_service_dependencies(business_service_id: str) -> BusinessServiceDependencyList:
    """Get dependencies for a business service.

    Uses GET /service_dependencies/business_services/{id} to return all service
    relationships where this business service is either the dependent or supporting service.

    Args:
        business_service_id: The ID of the business service

    Returns:
        BusinessServiceDependencyList containing the service relationships
    """
    client = get_client()
    resp = client.get(f"/service_dependencies/business_services/{business_service_id}")
    rels = resp.json().get("relationships", [])
    relationships = [Relationship(**rel) for rel in rels]
    return BusinessServiceDependencyList(relationships=relationships)
