from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import EscalationPolicy, EscalationPolicyCreate, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_escalation_policies(
    query: str | None = None,
    user_ids: list[str] | None = None,
    team_ids: list[str] | None = None,
    include: list[str] | None = None,
    limit: int | None = None,
) -> ListResponseModel[EscalationPolicy]:
    """List escalation policies with optional filtering.

    Args:
        query: Filter by name
        user_ids: Filter by user IDs
        team_ids: Filter by team IDs
        include: Additional details to include (e.g. services, teams)
        limit: Max results to return

    Returns:
        List of escalation policies matching the query parameters
    """
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    if user_ids:
        params["user_ids[]"] = user_ids
    if team_ids:
        params["team_ids[]"] = team_ids
    if include:
        params["include[]"] = include
    if limit:
        params["limit"] = limit
    response = paginate(client=get_client(), entity="escalation_policies", params=params)
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
    response = get_client().rpost("/escalation_policies", json=escalation_policy_data.model_dump(exclude_unset=True))

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
    response = get_client().rput(f"/escalation_policies/{policy_id}", json=escalation_policy_data.model_dump(exclude_unset=True))

    if type(response) is dict and "escalation_policy" in response:
        return EscalationPolicy.model_validate(response["escalation_policy"])

    return EscalationPolicy.model_validate(response)
