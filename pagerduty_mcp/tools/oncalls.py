from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Oncall,
    OncallQuery,
)
from pagerduty_mcp.utils import paginate


def list_oncalls(query_model: OncallQuery) -> ListResponseModel[Oncall]:
    """List on-call schedules with optional filtering.

    Returns:
        List of on-call schedules matching the query parameters
    """
    response = paginate(client=get_client(), entity="oncalls", params=query_model.to_params())
    oncalls = [Oncall(**oncall) for oncall in response]
    return ListResponseModel[Oncall](response=oncalls)
