from pagerduty_mcp.models import (
    IncidentWorkflow,
    IncidentWorkflowInstance,
    IncidentWorkflowInstanceRequest,
    IncidentWorkflowQuery,
    ListResponseModel,
    MCPContext,
)
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def list_incident_workflows(query_model: IncidentWorkflowQuery | None, context: MCPContext) -> ListResponseModel[IncidentWorkflow]:
    """List incident workflows with optional filtering.

    Args:
        query_model: Optional filtering parameters. If None, returns the first page with default limit of 100.
        context: The MCP context with client and user info (injected)

    Returns:
        List of IncidentWorkflow objects matching the query parameters
    """
    if query_model is None:
        query_model = IncidentWorkflowQuery()

    params = query_model.to_params()

    response = paginate(
        client=context.client,
        entity="incident_workflows",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    workflows = [IncidentWorkflow(**item) for item in response]
    return ListResponseModel[IncidentWorkflow](response=workflows)


@inject_context
def get_incident_workflow(workflow_id: str, context: MCPContext) -> IncidentWorkflow:
    """Get a specific incident workflow.

    Args:
        workflow_id: The ID of the incident workflow to retrieve
        context: The MCP context with client and user info (injected)

    Returns:
        IncidentWorkflow details
    """
    response = context.client.rget(f"/incident_workflows/{workflow_id}")

    if isinstance(response, dict) and "incident_workflow" in response:
        return IncidentWorkflow.model_validate(response["incident_workflow"])

    return IncidentWorkflow.model_validate(response)


@inject_context
def start_incident_workflow(
    workflow_id: str, instance_request: IncidentWorkflowInstanceRequest, context: MCPContext
) -> IncidentWorkflowInstance:
    """Start an incident workflow instance.

    Args:
        workflow_id: The ID of the workflow to start
        instance_request: The workflow instance request containing incident reference
        context: The MCP context with client and user info (injected)

    Returns:
        The created IncidentWorkflowInstance
    """
    response = context.client.rpost(
        f"/incident_workflows/{workflow_id}/instances",
        json=instance_request.model_dump(exclude_none=True),
    )

    if isinstance(response, dict) and "incident_workflow_instance" in response:
        return IncidentWorkflowInstance.model_validate(response["incident_workflow_instance"])

    return IncidentWorkflowInstance.model_validate(response)
