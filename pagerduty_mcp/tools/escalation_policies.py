import json
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import EscalationPolicy, ListResponseModel
from pagerduty_mcp.models.escalation_policies import EscalationPolicyCreate
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
        include: Include additional details (e.g. services, teams)
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
    response = paginate(
        client=get_client(), entity="escalation_policies", params=params
    )
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


def create_escalation_policy(escalation_policy: EscalationPolicyCreate) -> str:
    """Create a new escalation policy.

    Args:
        escalation_policy: The policy data to create

    Returns:
        JSON string of the created EscalationPolicy
    """
    payload = escalation_policy.model_dump(exclude_none=True)
    response = get_client().rpost(
        "/escalation_policies",
        json={"escalation_policy": payload},
    )
    return EscalationPolicy.model_validate(response).model_dump_json()


def update_escalation_policy(policy_id: str, escalation_policy: EscalationPolicyCreate) -> str:
    """Update an existing escalation policy.

    Args:
        policy_id: The ID of the escalation policy to update
        escalation_policy: The updated policy data

    Returns:
        JSON string of the updated EscalationPolicy
    """
    payload = escalation_policy.model_dump(exclude_none=True)
    response = get_client().rput(
        f"/escalation_policies/{policy_id}",
        json={"escalation_policy": payload},
    )
    return EscalationPolicy.model_validate(response).model_dump_json()


def delete_escalation_policy(policy_id: str) -> str:
    """Delete an escalation policy.

    Args:
        policy_id: The ID of the escalation policy to delete

    Returns:
        JSON string confirming deletion
    """
    get_client().rdelete(f"/escalation_policies/{policy_id}")
    return json.dumps({"success": True})
