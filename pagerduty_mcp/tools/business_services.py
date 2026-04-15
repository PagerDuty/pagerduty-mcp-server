import json

from pagerduty_mcp.client import get_client


def list_business_services() -> str:
    """List all business services.

    Returns:
        JSON string of business services
    """
    client = get_client()
    resp = client.get("/business_services", params={"limit": 100})
    data = resp.json()
    return json.dumps({"response": data.get("business_services", [])})


def get_business_service_dependencies(business_service_id: str) -> str:
    """Get dependencies for a business service.

    Args:
        business_service_id: The ID of the business service

    Returns:
        JSON string with relationships list
    """
    client = get_client()
    resp = client.get(f"/service_dependencies/business_services/{business_service_id}")
    data = resp.json()
    return json.dumps({"relationships": data.get("relationships", [])})
