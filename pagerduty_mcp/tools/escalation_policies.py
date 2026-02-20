from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import EscalationPolicy, EscalationPolicyQuery, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_escalation_policies(
    query_model: EscalationPolicyQuery,
) -> ListResponseModel[EscalationPolicy]:
    """List escalation policies with optional filtering.

    Returns:
        List of escalation policies matching the query parameters
    """
    response = paginate(client=get_client(), entity="escalation_policies", params=query_model.to_params())
    policies = [EscalationPolicy(**policy) for policy in response]
    return ListResponseModel[EscalationPolicy](response=policies)


def get_escalation_policy(policy_id: str) -> EscalationPolicy:
    """Get a specific escalation policy.

    Args:
        policy_id: The ID of the escalation policy to retrieve

    Returns:
        Escalation policy details
    """
    response = get_client().rget(f"/escalation_policies/{policy_id}")
    return EscalationPolicy.model_validate(response)
