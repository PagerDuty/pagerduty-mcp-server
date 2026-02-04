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


def list_incidents(query_model: IncidentQuery) -> str:
    """List incidents with optional filtering.

    Args:
        query_model: Optional filtering parameters

    Returns:
        JSON string of ListResponseModel containing Incident objects
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
    return ListResponseModel[Incident](response=incidents).model_dump_json()


def get_incident(incident_id: str) -> str:
    """Get a specific incident.

    Args:
        incident_id: The ID or number of the incident to retrieve.

    Returns:
        JSON string of Incident details
    """
    response = get_client().rget(f"/incidents/{incident_id}")
    return Incident.model_validate(response).model_dump_json()

def create_incident(create_model: IncidentCreateRequest) -> str:
    """Create an incident.

    Returns:
        JSON string of the created incident
    """
    response = get_client().rpost("/incidents", json=create_model.model_dump(exclude_none=True))

    return Incident.model_validate(response).model_dump_json()


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


def _escalate_to_policy(incident_ids: list[str], policy_id: str):
    request_payload = _generate_manage_request(incident_ids)
    request_payload = _update_manage_request(
        request_payload,
        "escalation_policy",
        {"type": "escalation_policy_reference", "id": policy_id},
    )

    return get_client().rput("/incidents", json=request_payload)


def _change_incident_priority(incident_ids: list[str], priority_id: str):
    request_payload = _generate_manage_request(incident_ids)
    request_payload = _update_manage_request(
        request_payload,
        "priority",
        {"type": "priority_reference", "id": priority_id},
    )

    return get_client().rput("/incidents", json=request_payload)


# TODO: Currently only supporting managing a single incident at a time.
# consider refactoring to support multiple incidents in the future.
def manage_incidents(
    manage_request: IncidentManageRequest,
) -> str:
    """Manage one or more incidents by changing its status, urgency, priority, assignment, or escalation level.

    Use this tool when you want to bulk update incidents.

    Args:
        manage_request: The request model containing the incident IDs and the fields to update
            (status, urgency, priority, assignment, escalation level)

    Returns:
        JSON string of ListResponseModel containing updated Incident objects
    """
    response = None
    if manage_request.status:
        response = _change_incident_status(manage_request.incident_ids, manage_request.status)
    if manage_request.urgency:
        response = _change_incident_urgency(manage_request.incident_ids, manage_request.urgency)
    if manage_request.priority:
        response = _change_incident_priority(manage_request.incident_ids, manage_request.priority.id)
    if manage_request.assignement:
        response = _reassign_incident(manage_request.incident_ids, manage_request.assignement)
    if manage_request.escalation_level:
        response = _escalate_incident(manage_request.incident_ids, manage_request.escalation_level)
    if manage_request.escalation_policy_id:
        response = _escalate_to_policy(manage_request.incident_ids, manage_request.escalation_policy_id)

    # TODO: Reconsider approach - We're overwriting the response
    if response:
        incidents = [Incident(**incident) for incident in response]
        return ListResponseModel[Incident](response=incidents).model_dump_json()
    return ListResponseModel[Incident](response=[]).model_dump_json()


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


def list_incident_notes(incident_id: str) -> str:
    """List all notes for a specific incident.

    Args:
        incident_id: The ID of the incident to retrieve notes from

    Returns:
        JSON string of ListResponseModel containing IncidentNote objects
    """
    response = get_client().rget(f"/incidents/{incident_id}/notes")

    # The rget method returns the unwrapped data directly (array of notes)
    if isinstance(response, list):
        notes = [IncidentNote.model_validate(note) for note in response]
        return ListResponseModel[IncidentNote](response=notes).model_dump_json()

    # Fallback if response format is unexpected
    return ListResponseModel[IncidentNote](response=[]).model_dump_json()


def add_note_to_incident(incident_id: str, note: str) -> str:
    """Add a note to an incident.

    Args:
        incident_id: The ID of the incident to add a note to
        note: The note text to be added
    Returns:
        JSON string of the updated incident with the new note
    """
    response = get_client().rpost(
        f"/incidents/{incident_id}/notes",
        json={"note": {"content": note}},
    )
    return IncidentNote.model_validate(response).model_dump_json()


def get_outlier_incident(incident_id: str, query_model: OutlierIncidentQuery) -> str:
    """Get Outlier Incident information for a given Incident on its Service.

    Outlier Incident returns incident that deviates from the expected patterns
    for the same Service. This feature is currently available as part of the
    Event Intelligence package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get outlier incident information for
        query_model: Query parameters including date range and additional details

    Returns:
        JSON string of outlier incident information
    """
    params = query_model.to_params()
    response = get_client().rget(f"/incidents/{incident_id}/outlier_incident", params=params)

    return OutlierIncidentResponse.from_api_response(response).model_dump_json()


def get_past_incidents(incident_id: str, query_model: PastIncidentsQuery) -> str:
    """Get Past Incidents related to a specific incident ID.

    Past Incidents returns Incidents within the past 6 months that have similar
    metadata and were generated on the same Service as the parent Incident.
    By default, 5 Past Incidents are returned. This feature is currently available
    as part of the Event Intelligence package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get past incidents for
        query_model: Query parameters including limit and total flag

    Returns:
        JSON string of past incidents with similarity scores
    """
    params = query_model.to_params()
    response = get_client().rget(f"/incidents/{incident_id}/past_incidents", params=params)

    return PastIncidentsResponse.from_api_response(response, default_limit=query_model.limit or 5).model_dump_json()


def get_related_incidents(incident_id: str, query_model: RelatedIncidentsQuery) -> str:
    """Get Related Incidents for a specific incident ID.

    Returns the 20 most recent Related Incidents that are impacting other Responders
    and Services. This feature is currently available as part of the Event Intelligence
    package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get related incidents for
        query_model: Query parameters including additional details

    Returns:
        JSON string of related incidents and their relationships
    """
    params = query_model.to_params()
    response = get_client().rget(f"/incidents/{incident_id}/related_incidents", params=params)

    return RelatedIncidentsResponse.from_api_response(response).model_dump_json()
