import os
import httpx
from pydantic import BaseModel
from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, Service, ServiceCreate, ServiceQuery
from pagerduty_mcp.utils import paginate
import uuid
from datetime import datetime, timezone


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

class ChatbotArgs(BaseModel):
    message: str
    incident_id: str

async def chatbot() -> dict:
    """Talk with PD Advance AI agent to generate a playbook.

    Make sure to extract the message and incident ID from user message

    Args:
        message (str): The text instruction for the AI agent.
        incident_id (str): REQUIRED. The PagerDuty incident ID (e.g. Q3Z2O4U38FLD1M).
            The LLM must always extract this ID from the user's request or ask
            the user to provide it if missing.

    Returns:
        Message from AI agent
    """
    ts = datetime.now(timezone.utc)
    formatted_timestamp = ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    payload = {
        "session_id": str(uuid.uuid4()),
        "timestamp": formatted_timestamp,
        # "message": args.message,
        # "incident_id": args.incident_id, # Q3Z2O4U38FLD1M
        "message": "Generate runbook",
        "incident_id": "Q3Z2O4U38FLD1M", # Q3Z2O4U38FLD1M
        "client_metadata": {
            "client_type": "public_api"
        }
    }

    API_KEY = os.getenv("PAGERDUTY_USER_API_KEY")
    headers = {
        "Authorization": f"Token token={API_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://api.pagerduty.com/chat_assistant/chat", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Error calling AI agent: {str(e)}",  # noqa: RUF010
            "data": None
        }
    except Exception as e:  # noqa: BLE001
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",  # noqa: RUF010
            "data": None
        }


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
