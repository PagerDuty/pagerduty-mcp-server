import json

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    EscalationPolicy,
    EscalationPolicyCreate,
    EscalationPolicyQuery,
    ListResponseModel,
)
from pagerduty_mcp.utils import paginate


def list_escalation_policies(
    query_model: EscalationPolicyQuery,
) -> str:
    """List escalation policies with optional filtering."""
    response = paginate(client=get_client(), entity="escalation_policies", params=query_model.to_params())
    policies = [EscalationPolicy(**policy) for policy in response]
    return ListResponseModel[EscalationPolicy](response=policies).model_dump_json()


def get_escalation_policy(policy_id: str) -> str:
    """Get a specific escalation policy."""
    response = get_client().rget(f"/escalation_policies/{policy_id}")
    return EscalationPolicy.model_validate(response).model_dump_json()


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
