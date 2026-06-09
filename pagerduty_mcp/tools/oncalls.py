from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Oncall,
    OncallQuery,
    Service,
)
from pagerduty_mcp.utils import paginate


def list_oncalls(query_model: OncallQuery | None = None) -> ListResponseModel[Oncall]:
    """List on-call schedules with optional filtering.

    Returns:
        List of on-call schedules matching the query parameters
    """
    if query_model is None:
        query_model = OncallQuery()
    client = get_client()
    params = query_model.to_params()

    # Resolve service_ids to escalation_policy_ids (not a native API parameter)
    if query_model.service_ids:
        ep_ids = list(params.get("escalation_policy_ids[]", []))
        for service_id in query_model.service_ids:
            service_response = client.rget(f"/services/{service_id}")
            service = Service.model_validate(service_response)
            ep_ids.append(service.escalation_policy.id)
        params["escalation_policy_ids[]"] = ep_ids

    response = paginate(client=client, entity="oncalls", params=params)
    oncalls = [Oncall(**oncall) for oncall in response]
    return ListResponseModel[Oncall](response=oncalls)
