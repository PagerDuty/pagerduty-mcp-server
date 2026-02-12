"""Alert Grouping Settings tools for the PagerDuty MCP server."""

from pagerduty_mcp.models import (
    AlertGroupingSetting,
    AlertGroupingSettingCreateRequest,
    AlertGroupingSettingQuery,
    AlertGroupingSettingUpdateRequest,
    ListResponseModel,
    MCPContext
)
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def list_alert_grouping_settings(query_model: AlertGroupingSettingQuery, context: MCPContext) -> ListResponseModel[AlertGroupingSetting]:
    """List all alert grouping settings with optional filtering.

    Args:
        context: The MCP context with client and user info (injected)
        query_model: Optional filtering parameters

    Returns:
        List of alert grouping settings matching the query parameters
    """
    params = query_model.to_params()

    response = paginate(
        client=context.client, entity="alert_grouping_settings", params=params, maximum_records=query_model.limit or 1000
    )

    settings = [AlertGroupingSetting(**setting) for setting in response]
    return ListResponseModel[AlertGroupingSetting](response=settings)


@inject_context
def get_alert_grouping_setting(setting_id: str, context: MCPContext) -> AlertGroupingSetting:
    """Get details for a specific alert grouping setting.

    Args:
        context: The MCP context with client and user info (injected)
        setting_id: The ID of the alert grouping setting to retrieve

    Returns:
        Alert grouping setting details
    """
    response = context.client.rget(f"/alert_grouping_settings/{setting_id}")

    # Handle wrapped response
    if isinstance(response, dict) and "alert_grouping_setting" in response:
        return AlertGroupingSetting.model_validate(response["alert_grouping_setting"])

    return AlertGroupingSetting.model_validate(response)


@inject_context
def create_alert_grouping_setting(create_model: AlertGroupingSettingCreateRequest, context: MCPContext) -> AlertGroupingSetting:
    """Create a new alert grouping setting.

    Args:
        context: The MCP context with client and user info (injected)
        create_model: The alert grouping setting creation request

    Returns:
        The created alert grouping setting
    """
    response = context.client.rpost("/alert_grouping_settings", json=create_model.model_dump(exclude_none=True))

    # Handle wrapped response
    if isinstance(response, dict) and "alert_grouping_setting" in response:
        return AlertGroupingSetting.model_validate(response["alert_grouping_setting"])

    return AlertGroupingSetting.model_validate(response)


@inject_context
def update_alert_grouping_setting(
    setting_id: str, update_model: AlertGroupingSettingUpdateRequest, context: MCPContext
) -> AlertGroupingSetting:
    """Update an existing alert grouping setting.

    Args:
        context: The MCP context with client and user info (injected)
        setting_id: The ID of the alert grouping setting to update
        update_model: The alert grouping setting update request

    Returns:
        The updated alert grouping setting
    """
    response = context.client.rput(
        f"/alert_grouping_settings/{setting_id}", json=update_model.model_dump(exclude_none=True)
    )

    # Handle wrapped response
    if isinstance(response, dict) and "alert_grouping_setting" in response:
        return AlertGroupingSetting.model_validate(response["alert_grouping_setting"])

    return AlertGroupingSetting.model_validate(response)


@inject_context
def delete_alert_grouping_setting(setting_id: str, context: MCPContext) -> None:
    """Delete an alert grouping setting.

    Args:
        context: The MCP context with client and user info (injected)
        setting_id: The ID of the alert grouping setting to delete

    Returns:
        None (successful deletion returns no content)
    """
    context.client.rdelete(f"/alert_grouping_settings/{setting_id}")
    # The API returns 204 No Content for successful deletion
