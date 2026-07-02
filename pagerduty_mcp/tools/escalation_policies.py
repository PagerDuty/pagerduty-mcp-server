from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import EscalationPolicy, ListResponseModel
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
