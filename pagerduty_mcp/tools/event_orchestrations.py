from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    EventOrchestration,
    EventOrchestrationGlobal,
    EventOrchestrationQuery,
    EventOrchestrationRouter,
    EventOrchestrationRouterUpdateRequest,
    EventOrchestrationRuleCreateRequest,
    EventOrchestrationService,
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

    return EventOrchestrationRouter.from_api_response(response)


def update_event_orchestration_router(
    orchestration_id: str, router_update: EventOrchestrationRouterUpdateRequest
) -> EventOrchestrationRouter:
    """Update the router configuration for a specific event orchestration.

    Args:
        orchestration_id: The ID of the event orchestration to update router for
        router_update: The updated router configuration

    Returns:
        The updated event orchestration router configuration
    """
    response = get_client().rput(f"/event_orchestrations/{orchestration_id}/router", json=router_update.model_dump())

    return EventOrchestrationRouter.from_api_response(response)


def append_event_orchestration_router_rule(
    orchestration_id: str, new_rule: EventOrchestrationRuleCreateRequest
) -> EventOrchestrationRouter:
    """Append a new routing rule to the end of an event orchestration's router rules.

    This function first retrieves the current router configuration, appends the new rule
    to the existing rules array, and then updates the router configuration.

    Args:
        orchestration_id: The ID of the event orchestration to append rule to
        new_rule: The new rule configuration to append

    Returns:
        The updated event orchestration router configuration with the new rule appended
    """
    from pagerduty_mcp.models.event_orchestrations import EventOrchestrationRule

    current_router = get_event_orchestration_router(orchestration_id)

    if not current_router.orchestration_path or not current_router.orchestration_path.sets:
        raise ValueError(f"Event orchestration {orchestration_id} has no valid router configuration")

    rule_set = current_router.orchestration_path.sets[0]

    new_rule_data = new_rule.model_dump()
    new_rule_data["id"] = "temp_id_will_be_replaced_by_api"
    new_rule_obj = EventOrchestrationRule.model_validate(new_rule_data)

    updated_rules = list(rule_set.rules) if rule_set.rules else []
    updated_rules.append(new_rule_obj)

    updated_rule_set = rule_set.model_copy()
    updated_rule_set.rules = updated_rules

    updated_path = current_router.orchestration_path.model_copy()
    updated_path.sets = [updated_rule_set]

    update_request = EventOrchestrationRouterUpdateRequest.from_path(updated_path)

    return update_event_orchestration_router(orchestration_id, update_request)


def get_event_orchestration_service(service_id: str) -> EventOrchestrationService:
    """Get the Service Orchestration configuration for a specific service.

    Args:
        service_id: The ID of the service to retrieve the orchestration configuration for

    Returns:
        The service orchestration configuration
    """
    response = get_client().jget(f"/event_orchestrations/services/{service_id}")

    return EventOrchestrationService.from_api_response(response)


def get_event_orchestration_global(orchestration_id: str) -> EventOrchestrationGlobal:
    """Get the Global Orchestration configuration for a specific event orchestration.

    Args:
        orchestration_id: The ID of the event orchestration to retrieve global configuration for

    Returns:
        The global orchestration configuration
    """
    response = get_client().rget(f"/event_orchestrations/{orchestration_id}/global")

    return EventOrchestrationGlobal.from_api_response(response)
