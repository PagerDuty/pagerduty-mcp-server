from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    EventOrchestration,
    EventOrchestrationQuery,
    EventOrchestrationRouter,
    ListResponseModel,
)
from pagerduty_mcp.utils import paginate


def list_event_orchestrations(query_model: EventOrchestrationQuery) -> ListResponseModel[EventOrchestration]:
    """List event orchestrations with optional filtering.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of event orchestrations matching the query parameters
    """
    response = paginate(client=get_client(), entity="event_orchestrations", params=query_model.to_params())
    orchestrations = [EventOrchestration(**orchestration) for orchestration in response]
    return ListResponseModel[EventOrchestration](response=orchestrations)


def get_event_orchestration(orchestration_id: str) -> EventOrchestration:
    """Get details for a specific event orchestration.

    Args:
        orchestration_id: The ID of the event orchestration to retrieve

    Returns:
        The event orchestration details
    """
    response = get_client().rget(f"/event_orchestrations/{orchestration_id}")

    if isinstance(response, dict) and "orchestration" in response:
        return EventOrchestration.model_validate(response["orchestration"])

    return EventOrchestration.model_validate(response)


def get_event_orchestration_router(orchestration_id: str) -> EventOrchestrationRouter:
    """Get the router configuration for a specific event orchestration.

    Args:
        orchestration_id: The ID of the event orchestration to retrieve router for

    Returns:
        The event orchestration router configuration
    """
    response = get_client().rget(f"/event_orchestrations/{orchestration_id}/router")

    # Use the new factory method to handle both response formats
    return EventOrchestrationRouter.from_api_response(response)
