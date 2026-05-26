from typing import Any, Literal

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    IncidentWorkflow,
    IncidentWorkflowInstance,
    IncidentWorkflowInstanceRequest,
    ListResponseModel,
)
from pagerduty_mcp.utils import paginate


def list_incident_workflows(
    limit: int | None = 100,
    query: str | None = None,
    include: list[Literal["steps", "team"]] | None = None,
) -> ListResponseModel[IncidentWorkflow]:
    """List incident workflows with optional filtering.

    Args:
        limit: Maximum number of results to return. Maximum is 100. Default 100.
        query: Filters the result, showing only the records whose name matches the query.
        include: Array of additional details to include. Options: 'steps', 'team'.

    Returns:
        List of IncidentWorkflow objects matching the query parameters
    """
    params: dict[str, Any] = {}
    if limit:
        params["limit"] = limit
    if query:
        params["query"] = query
    if include:
        params["include[]"] = include

    response = paginate(
        client=get_client(),
        entity="incident_workflows",
        params=params,
        maximum_records=limit or 100,
    )

    workflows = [IncidentWorkflow(**item) for item in response]
    return ListResponseModel[IncidentWorkflow](response=workflows)


def get_incident_workflow(workflow_id: str) -> IncidentWorkflow:
    """Get a specific incident workflow.

    Args:
        workflow_id: The ID of the incident workflow to retrieve

    Returns:
        IncidentWorkflow details
    """
    response = get_client().rget(f"/incident_workflows/{workflow_id}")

    if isinstance(response, dict) and "incident_workflow" in response:
        return IncidentWorkflow.model_validate(response["incident_workflow"])

    return IncidentWorkflow.model_validate(response)


def start_incident_workflow(
    workflow_id: str, instance_request: IncidentWorkflowInstanceRequest
) -> IncidentWorkflowInstance:
    """Start an incident workflow instance.

    Args:
        workflow_id: The ID of the workflow to start
        instance_request: The workflow instance request containing incident reference

    Returns:
        The created IncidentWorkflowInstance
    """
    response = get_client().rpost(
        f"/incident_workflows/{workflow_id}/instances",
        json=instance_request.model_dump(exclude_none=True),
    )

    if isinstance(response, dict) and "incident_workflow_instance" in response:
        return IncidentWorkflowInstance.model_validate(response["incident_workflow_instance"])

    return IncidentWorkflowInstance.model_validate(response)
