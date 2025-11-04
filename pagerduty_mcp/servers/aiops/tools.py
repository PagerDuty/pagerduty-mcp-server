"""Tools for PagerDuty AIOps MCP Server.

This module consolidates tools from:
- Alert Grouping Settings (5 tools)
- Event Orchestrations (7 tools)
"""

from pagerduty_mcp.common import get_client, paginate
from .models import (
    AlertGroupingSetting,
    AlertGroupingSettingQuery,
    AppendRouterRuleRequest,
    CreateAlertGroupingSettingRequest,
    EventOrchestration,
    EventOrchestrationGlobal,
    EventOrchestrationQuery,
    EventOrchestrationRouter,
    EventOrchestrationRouterUpdateRequest,
    EventOrchestrationService,
    ListResponseModel,
    UpdateAlertGroupingSettingRequest,
)


# =============================================================================
# ALERT GROUPING SETTINGS TOOLS
# =============================================================================


def list_alert_grouping_settings(query_model: AlertGroupingSettingQuery) -> ListResponseModel[AlertGroupingSetting]:
    """List all alert grouping settings with optional filtering.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of alert grouping settings matching the query parameters
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(), entity="alert_grouping_settings", params=params, maximum_records=query_model.limit or 1000
    )

    settings = [AlertGroupingSetting(**setting) for setting in response]
    return ListResponseModel[AlertGroupingSetting](response=settings)


def get_alert_grouping_setting(setting_id: str) -> AlertGroupingSetting:
    """Get details for a specific alert grouping setting.

    Args:
        setting_id: The ID of the alert grouping setting to retrieve

    Returns:
        Alert grouping setting details
    """
    response = get_client().rget(f"/alert_grouping_settings/{setting_id}")

    if isinstance(response, dict) and "alert_grouping_setting" in response:
        return AlertGroupingSetting.model_validate(response["alert_grouping_setting"])

    return AlertGroupingSetting.model_validate(response)


def create_alert_grouping_setting(create_model: CreateAlertGroupingSettingRequest) -> AlertGroupingSetting:
    """Create a new alert grouping setting.

    Args:
        create_model: The alert grouping setting creation request

    Returns:
        The created alert grouping setting
    """
    response = get_client().rpost("/alert_grouping_settings", json=create_model.model_dump(exclude_none=True))

    if isinstance(response, dict) and "alert_grouping_setting" in response:
        return AlertGroupingSetting.model_validate(response["alert_grouping_setting"])

    return AlertGroupingSetting.model_validate(response)


def update_alert_grouping_setting(
    setting_id: str, update_model: UpdateAlertGroupingSettingRequest
) -> AlertGroupingSetting:
    """Update an existing alert grouping setting.

    Args:
        setting_id: The ID of the alert grouping setting to update
        update_model: The alert grouping setting update request

    Returns:
        The updated alert grouping setting
    """
    response = get_client().rput(
        f"/alert_grouping_settings/{setting_id}", json=update_model.model_dump(exclude_none=True)
    )

    if isinstance(response, dict) and "alert_grouping_setting" in response:
        return AlertGroupingSetting.model_validate(response["alert_grouping_setting"])

    return AlertGroupingSetting.model_validate(response)


def delete_alert_grouping_setting(setting_id: str) -> None:
    """Delete an alert grouping setting.

    Args:
        setting_id: The ID of the alert grouping setting to delete

    Returns:
        None (successful deletion returns no content)
    """
    get_client().rdelete(f"/alert_grouping_settings/{setting_id}")


# =============================================================================
# EVENT ORCHESTRATION TOOLS
# =============================================================================


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
    orchestration_id: str, new_rule: AppendRouterRuleRequest
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
    from .models import EventOrchestrationRule

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


# =============================================================================
# TOOL LISTS
# =============================================================================

READ_TOOLS = [
    # Alert Grouping Settings (2)
    list_alert_grouping_settings,
    get_alert_grouping_setting,
    # Event Orchestrations (5)
    list_event_orchestrations,
    get_event_orchestration,
    get_event_orchestration_router,
    get_event_orchestration_service,
    get_event_orchestration_global,
]

WRITE_TOOLS = [
    # Alert Grouping Settings (3)
    create_alert_grouping_setting,
    update_alert_grouping_setting,
    delete_alert_grouping_setting,
    # Event Orchestrations (2)
    update_event_orchestration_router,
    append_event_orchestration_router_rule,
]
