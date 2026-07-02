from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    EventOrchestration,
    EventOrchestrationGlobal,
    EventOrchestrationGlobalUpdateRequest,
    EventOrchestrationQuery,
    EventOrchestrationRouter,
    EventOrchestrationRouterUpdateRequest,
    EventOrchestrationRuleCreateRequest,
    EventOrchestrationService,
    EventOrchestrationServiceUpdateRequest,
    EventOrchestrationUnrouted,
    EventOrchestrationUnroutedUpdateRequest,
    ListResponseModel,
)
from pagerduty_mcp.utils import paginate


def list_event_orchestrations(
    query_model: EventOrchestrationQuery | None = None,
) -> ListResponseModel[EventOrchestration]:
    """List event orchestrations with optional filtering.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of event orchestrations matching the query parameters
    """
    if query_model is None:
        query_model = EventOrchestrationQuery()
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


def update_event_orchestration_global(
    orchestration_id: str, global_update: EventOrchestrationGlobalUpdateRequest
) -> EventOrchestrationGlobal:
    """Update the Global Orchestration rules for an event orchestration.

    Performs a full replacement of the global orchestration path (all rule sets and
    catch_all). Retrieve the current configuration with get_event_orchestration_global,
    modify it, and pass the full updated set of rules.

    Rule conditions use PCL expressions, e.g. "event.summary matches part 'timeout'".

    Args:
        orchestration_id: The ID of the event orchestration to update global rules for
        global_update: The full updated global orchestration configuration

    Returns:
        The updated global orchestration configuration
    """
    response = get_client().rput(
        f"/event_orchestrations/{orchestration_id}/global", json=global_update.model_dump(exclude_none=True)
    )
    return EventOrchestrationGlobal.from_api_response(response)


def update_event_orchestration_unrouted(
    orchestration_id: str, unrouted_update: EventOrchestrationUnroutedUpdateRequest
) -> EventOrchestrationUnrouted:
    """Update the Unrouted Orchestration rules for an event orchestration.

    Unrouted rules handle events that did not match any routing condition. Performs a
    full replacement of the unrouted path. Retrieve the current configuration first,
    modify it, and pass the full updated set of rules.

    Rule conditions use PCL expressions, e.g. "event.severity matches 'critical'".

    Args:
        orchestration_id: The ID of the event orchestration to update unrouted rules for
        unrouted_update: The full updated unrouted orchestration configuration

    Returns:
        The updated unrouted orchestration configuration
    """
    response = get_client().rput(
        f"/event_orchestrations/{orchestration_id}/unrouted", json=unrouted_update.model_dump(exclude_none=True)
    )
    return EventOrchestrationUnrouted.from_api_response(response)


def update_event_orchestration_service(
    service_id: str, service_update: EventOrchestrationServiceUpdateRequest
) -> EventOrchestrationService:
    """Update the Service Orchestration rules for a specific service.

    Performs a full replacement of the service orchestration path. Retrieve the current
    configuration with get_event_orchestration_service, modify it, and pass the full
    updated set of rules. Rule conditions use PCL expressions.

    Args:
        service_id: The ID of the service to update orchestration rules for
        service_update: The full updated service orchestration configuration

    Returns:
        The updated service orchestration configuration
    """
    response = get_client().rput(
        f"/event_orchestrations/services/{service_id}", json=service_update.model_dump(exclude_none=True)
    )
    return EventOrchestrationService.from_api_response(response)


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
