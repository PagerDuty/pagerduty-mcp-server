from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    IncidentWorkflow,
    IncidentWorkflowInstance,
    IncidentWorkflowInstanceRequest,
    IncidentWorkflowQuery,
    ListResponseModel,
)
from pagerduty_mcp.utils import paginate


def list_incident_workflows(query_model: IncidentWorkflowQuery | None = None) -> ListResponseModel[IncidentWorkflow]:
    """List incident workflows with optional filtering.

    Args:
        query_model: Optional filtering parameters. If None, returns the first page with default limit of 100.

    Returns:
        List of IncidentWorkflow objects matching the query parameters
    """
    if query_model is None:
        query_model = IncidentWorkflowQuery()

    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity="incident_workflows",
        params=params,
        maximum_records=query_model.limit or 100,
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
