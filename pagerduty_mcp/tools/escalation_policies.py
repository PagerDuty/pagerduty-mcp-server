from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import EscalationPolicy, EscalationPolicyCreate, EscalationPolicyQuery, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_escalation_policies(
    query_model: EscalationPolicyQuery | None = None,
) -> ListResponseModel[EscalationPolicy]:
    """List escalation policies with optional filtering.

    Returns:
        List of escalation policies matching the query parameters
    """
    if query_model is None:
        query_model = EscalationPolicyQuery()
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


def create_escalation_policy(escalation_policy_data: EscalationPolicyCreate) -> EscalationPolicy:
    """Create a new escalation policy.

    Args:
        escalation_policy_data: The data for the new escalation policy. Do not include the ID
            since it is auto-generated. Each escalation rule requires at least one target
            with 'id' and 'type' (user_reference or schedule_reference).

    Returns:
        The created escalation policy
    """
    response = get_client().rpost("/escalation_policies", json=escalation_policy_data.model_dump())

    if type(response) is dict and "escalation_policy" in response:
        return EscalationPolicy.model_validate(response["escalation_policy"])

    return EscalationPolicy.model_validate(response)


def update_escalation_policy(policy_id: str, escalation_policy_data: EscalationPolicyCreate) -> EscalationPolicy:
    """Update an existing escalation policy.

    Args:
        policy_id: The ID of the escalation policy to update
        escalation_policy_data: The updated escalation policy data

    Returns:
        The updated escalation policy
    """
    response = get_client().rput(f"/escalation_policies/{policy_id}", json=escalation_policy_data.model_dump())

    if type(response) is dict and "escalation_policy" in response:
        return EscalationPolicy.model_validate(response["escalation_policy"])

    return EscalationPolicy.model_validate(response)
