from datetime import datetime
from typing import Any

from mcp.server.fastmcp import Context

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    Incident,
    IncidentCreateRequest,
    IncidentManageRequest,
    IncidentNote,
    IncidentQuery,
    IncidentResponderRequest,
    IncidentResponderRequestResponse,
    ListResponseModel,
    MCPContext,
    OutlierIncidentQuery,
    OutlierIncidentResponse,
    PastIncidentsQuery,
    PastIncidentsResponse,
    RelatedIncidentsQuery,
    RelatedIncidentsResponse,
    UserReference,
)
from pagerduty_mcp.tools.users import get_user_data
from pagerduty_mcp.utils import paginate


def list_incidents(query_model: IncidentQuery) -> ListResponseModel[Incident]:
    """List incidents with optional filtering.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of Incident objects matching the query parameters

    Examples:
        Basic usage filtering by status:

        >>> from pagerduty_mcp.models import IncidentQuery
        >>> result = list_incidents(IncidentQuery(status=["triggered"]))
        >>> isinstance(result.response, list)
        True

        Multiple statuses with a limit:

        >>> result = list_incidents(IncidentQuery(status=["triggered", "acknowledged"], limit=10))
    """
    params = query_model.to_params()

    if query_model.request_scope in ["assigned", "teams"]:
        user_data = get_user_data()

        if query_model.request_scope == "assigned":
            params["user_ids[]"] = [user_data.id]
        elif query_model.request_scope == "teams":
            user_team_ids = [team.id for team in user_data.teams]
            params["teams_ids[]"] = user_team_ids

    response = paginate(
        client=get_client(), entity="incidents", params=params, maximum_records=query_model.limit or 100
    )
    incidents = [Incident(**incident) for incident in response]
    return ListResponseModel[Incident](response=incidents)


def get_incident(incident_id: str) -> Incident:
    """Get a specific incident.

    Args:
        incident_id: The ID or number of the incident to retrieve.

    Returns:
        Incident details
    """
    response = get_client().rget(f"/incidents/{incident_id}")
    return Incident.model_validate(response)


def create_incident(create_model: IncidentCreateRequest) -> Incident:
    """Create an incident.

    Returns:
        The created incident
    """
    response = get_client().rpost("/incidents", json=create_model.model_dump(exclude_none=True))

    return Incident.model_validate(response)


def _generate_manage_request(incident_ids: list[str]):
    incident_references = []
    for incident_id in incident_ids:
        incident_references.append(
            {
                "type": "incident_reference",
                "id": incident_id,
            }
        )
    return {"incidents": incident_references}


def _update_manage_request(request: dict, field_name: str, field_value: Any):
    for incident_reference in request["incidents"]:
        incident_reference[field_name] = field_value

    return request


def _reassign_incident(incident_ids: list[str], assignee: UserReference):
    request_payload = _generate_manage_request(incident_ids)
    assignment_data = [
        {
            "at": datetime.now().isoformat(),
            "assignee": {
                "type": "user_reference",
                "id": assignee.id,
            },
        }
    ]
    request_payload = _update_manage_request(request_payload, "assignments", assignment_data)

    return get_client().rput("/incidents", json=request_payload)


def _change_incident_status(incident_ids: list[str], status: str):
    request_payload = _generate_manage_request(incident_ids)
    request_payload = _update_manage_request(request_payload, "status", status)

    return get_client().rput("/incidents", json=request_payload)


def _change_incident_urgency(incident_ids: list[str], urgency: str):
    request_payload = _generate_manage_request(incident_ids)
    request_payload = _update_manage_request(request_payload, "urgency", urgency)

    return get_client().rput("/incidents", json=request_payload)


def _escalate_incident(incident_ids: list[str], level: int):
    request_payload = _generate_manage_request(incident_ids)
    request_payload = _update_manage_request(request_payload, "escalation_level", level)

    return get_client().rput("/incidents", json=request_payload)


# TODO: Currently only supporting managing a single incident at a time.
# consider refactoring to support multiple incidents in the future.
def manage_incidents(
    manage_request: IncidentManageRequest,
) -> ListResponseModel[Incident]:
    """Manage one or more incidents by changing its status, urgency, assignment, or escalation level.

    Use this tool when you want to bulk update incidents.

    Args:
        manage_request: The request model containing the incident IDs and the fields to update
            (status, urgency, assignment, escalation level)

    Returns:
        The updated incident
    """
    response = None
    if manage_request.status:
        response = _change_incident_status(manage_request.incident_ids, manage_request.status)
    if manage_request.urgency:
        response = _change_incident_urgency(manage_request.incident_ids, manage_request.urgency)
    if manage_request.assignement:
        response = _reassign_incident(manage_request.incident_ids, manage_request.assignement)
    if manage_request.escalation_level:
        response = _escalate_incident(manage_request.incident_ids, manage_request.escalation_level)

    # TODO: Reconsider approach - We're overwriting the response
    if response:
        incidents = [Incident(**incident) for incident in response]
        return ListResponseModel[Incident](response=incidents)
    return ListResponseModel[Incident](response=[])


def add_responders(
    incident_id: str, request: IncidentResponderRequest, ctx: Context
) -> IncidentResponderRequestResponse | str:
    """Add responders to an incident.

    Args:
        incident_id: The ID of the incident to add responders to
        request: The responder request data containing user IDs and optional message
        ctx: The context containing the request information

    Returns:
        Details of the responder request
    """
    context_info: MCPContext = ctx.request_context.lifespan_context
    if context_info.user is None:
        return "Cannot add responders with account level auth. Please provide a user token."

    requester_id = context_info.user.id
    request.requester_id = requester_id

    response = get_client().rpost(f"/incidents/{incident_id}/responder_requests", json=request.model_dump())
    if type(response) is dict and "responder_request" in response:
        # If the response is a dict with a responder_request key, return the model
        return IncidentResponderRequestResponse.model_validate(response["responder_request"])
    return "Unexpected response format: " + str(response)


def add_note_to_incident(incident_id: str, note: str) -> IncidentNote:
    """Add a note to an incident.

    Args:
        incident_id: The ID of the incident to add a note to
        note: The note text to be added
    Returns:
        The updated incident with the new note
    """
    response = get_client().rpost(
        f"/incidents/{incident_id}/notes",
        json={"note": {"content": note}},
    )
    return IncidentNote.model_validate(response)


def get_outlier_incident(incident_id: str, query_model: OutlierIncidentQuery) -> OutlierIncidentResponse:
    """Get Outlier Incident information for a given Incident on its Service.

    Outlier Incident returns incident that deviates from the expected patterns
    for the same Service. This feature is currently available as part of the
    Event Intelligence package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get outlier incident information for
        query_model: Query parameters including date range and additional details

    Returns:
        Outlier incident information calculated over the same Service as the given Incident
    """
    params = query_model.to_params()
    response = get_client().rget(f"/incidents/{incident_id}/outlier_incident", params=params)

    return OutlierIncidentResponse.from_api_response(response)


def get_past_incidents(incident_id: str, query_model: PastIncidentsQuery) -> PastIncidentsResponse:
    """Get Past Incidents related to a specific incident ID.

    Past Incidents returns Incidents within the past 6 months that have similar
    metadata and were generated on the same Service as the parent Incident.
    By default, 5 Past Incidents are returned. This feature is currently available
    as part of the Event Intelligence package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get past incidents for
        query_model: Query parameters including limit and total flag

    Returns:
        List of past incidents with similarity scores
    """
    params = query_model.to_params()
    response = get_client().rget(f"/incidents/{incident_id}/past_incidents", params=params)

    return PastIncidentsResponse.from_api_response(response, default_limit=query_model.limit or 5)


def get_related_incidents(incident_id: str, query_model: RelatedIncidentsQuery) -> RelatedIncidentsResponse:
    """Get Related Incidents for a specific incident ID.

    Returns the 20 most recent Related Incidents that are impacting other Responders
    and Services. This feature is currently available as part of the Event Intelligence
    package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get related incidents for
        query_model: Query parameters including additional details

    Returns:
        List of related incidents and their relationships
    """
    params = query_model.to_params()
    response = get_client().rget(f"/incidents/{incident_id}/related_incidents", params=params)

    return RelatedIncidentsResponse.from_api_response(response)
