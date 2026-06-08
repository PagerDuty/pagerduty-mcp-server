from datetime import datetime
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Oncall,
    Service,
)
from pagerduty_mcp.utils import paginate


def list_oncalls(
    time_zone: str | None = None,
    user_ids: list[str] | None = None,
    escalation_policy_ids: list[str] | None = None,
    schedule_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    earliest: bool | None = True,
    limit: int | None = None,
) -> ListResponseModel[Oncall]:
    """List on-call schedules with optional filtering.

    Args:
        time_zone: Time zone for date rendering (e.g. America/New_York)
        user_ids: Filter by user IDs
        escalation_policy_ids: Filter by escalation policy IDs
        schedule_ids: Filter by schedule IDs
        service_ids: Filter by service IDs. Resolves each service to its escalation policy to find on-call responders.
        since: Start of time range
        until: End of time range
        earliest: Return only earliest oncall per user/policy combination. Defaults to True.
        limit: Max results to return

    Returns:
        List of on-call schedules matching the query parameters
    """
    client = get_client()
    params: dict[str, Any] = {}
    if time_zone:
        params["time_zone"] = time_zone
    if user_ids:
        params["user_ids[]"] = user_ids
    if escalation_policy_ids:
        params["escalation_policy_ids[]"] = escalation_policy_ids
    if schedule_ids:
        params["schedule_ids[]"] = schedule_ids
    if since:
        params["since"] = since.isoformat()
    if until:
        params["until"] = until.isoformat()
    if earliest is not None:
        params["earliest"] = str(earliest).lower()
    if limit is not None:
        params["limit"] = limit

    # Resolve service_ids to escalation_policy_ids (not a native API parameter)
    if service_ids:
        ep_ids = list(params.get("escalation_policy_ids[]", []))
        for service_id in service_ids:
            service_response = client.rget(f"/services/{service_id}")
            service = Service.model_validate(service_response)
            ep_ids.append(service.escalation_policy.id)
        params["escalation_policy_ids[]"] = ep_ids

    response = paginate(
        client=client, entity="oncalls", params=params, maximum_records=limit or 1000
    )
    oncalls = [Oncall(**oncall) for oncall in response]
    return ListResponseModel[Oncall](response=oncalls)
