from pagerduty_mcp.models import (
    ListResponseModel,
    MCPContext,
    Oncall,
    OncallQuery,
)
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def list_oncalls(query_model: OncallQuery, context: MCPContext) -> ListResponseModel[Oncall]:
    """List on-call schedules with optional filtering.

    Args:
        query_model: Optional filtering parameters
        context: The MCP context with client and user info (injected)

    Returns:
        List of on-call schedules matching the query parameters
    """
    response = paginate(client=context.client, entity="oncalls", params=query_model.to_params())
    oncalls = [Oncall(**oncall) for oncall in response]
    return ListResponseModel[Oncall](response=oncalls)
