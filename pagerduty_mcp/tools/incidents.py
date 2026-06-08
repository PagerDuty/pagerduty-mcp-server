import json
from datetime import datetime
from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.context import ContextResolver
from pagerduty_mcp.models import (
    MAX_RESULTS,
    Incident,
    IncidentCreate,
    IncidentManageRequest,
    IncidentNote,
    IncidentResponderRequest,
    IncidentResponderRequestResponse,
    ListResponseModel,
    OutlierIncidentResponse,
    PastIncidentsResponse,
    RelatedIncidentsResponse,
    UserReference,
)
from pagerduty_mcp.utils import paginate


def list_incidents(
    statuses: list[str] | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    user_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    team_ids: list[str] | None = None,
    urgencies: list[str] | None = None,
    sort_by: list[str] | None = None,
    request_scope: str | None = None,
    limit: int | None = None,
) -> ListResponseModel[Incident]:
    """List incidents with optional filtering.

    Args:
        statuses: Filter by status (triggered, acknowledged, resolved).
            Note: "open" incidents include BOTH "triggered" and "acknowledged" statuses.
            To list all open incidents pass statuses=["triggered", "acknowledged"].
        since: Filter incidents since a specific date
        until: Filter incidents until a specific date
        user_ids: Filter by user IDs
        service_ids: Filter by service IDs
        team_ids: Filter by team IDs
        urgencies: Filter by urgency (high, low)
        sort_by: Sort fields and directions (e.g. ['created_at:desc'])
        request_scope: 'all', 'teams' (my teams), or 'assigned' (assigned to me)
        limit: Max results to return

    Returns:
        List of incidents matching the query parameters
    """
    params: dict[str, Any] = {}
    if statuses:
        params["statuses[]"] = statuses
    if since:
        params["since"] = since.isoformat()
    if until:
        params["until"] = until.isoformat()
    if service_ids:
        params["service_ids[]"] = service_ids
    if team_ids:
        params["team_ids[]"] = team_ids
    if user_ids:
        params["user_ids[]"] = user_ids
    if urgencies:
        params["urgencies[]"] = urgencies
    if sort_by:
        params["sort_by"] = ",".join(sort_by)

    if request_scope in ["assigned", "teams"]:
        user_data = ContextResolver.get_user()
        if user_data is None:
            raise ValueError(
                f'Cannot filter incidents by "{request_scope}" with account-level auth. '
                "Please provide a user token, or scope the request differently."
            )

        if request_scope == "assigned":
            params["user_ids[]"] = [user_data.id]
        elif request_scope == "teams":
            user_team_ids = [team.id for team in user_data.teams]
            params["team_ids[]"] = user_team_ids

    response = paginate(
        client=ContextResolver.get_client(), entity="incidents", params=params, maximum_records=limit or MAX_RESULTS
    )
    incidents = [Incident(**incident) for incident in response]
    return ListResponseModel[Incident](response=incidents)


def get_incident(
    incident_id: str,
    include: list[str] | None = None,
) -> Incident:
    """Get a specific incident.

    Args:
        incident_id: The ID or number of the incident to retrieve.
        include: List of additional information to include in the response.
            Available options: 'users', 'services', 'assignments', 'acknowledgers',
            'custom_fields', 'teams', 'escalation_policies', 'log_entries', 'notes',
            'urgencies', 'priorities', 'external_references', 'metadata'.
            Use 'external_references' to include external system integration links such as
            ServiceNow, Zendesk, and other third-party integrations associated with the incident.
            Use 'metadata' to include additional metadata associated with the incident.
            Use 'log_entries' to include the incident's log/audit entries inline (do NOT call
            list_log_entries separately when this option suffices).

    Returns:
        Incident details
    """
    params: dict[str, Any] = {}
    if include:
        params["include[]"] = include
    response = get_client().rget(f"/incidents/{incident_id}", params=params)
    return Incident.model_validate(response)


def create_incident(incident: IncidentCreate) -> Incident:
    """Create an incident.

    Returns:
        The created incident
    """
    response = get_client().rpost("/incidents", json={"incident": incident.model_dump(exclude_none=True)})

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

    This tool accepts flat fields on the manage_request model: 'incident_ids' (list of IDs),
    plus optional 'status', 'urgency', 'assignment' (UserReference with 'id'), and
    'escalation_level' (int). It does NOT use the nested PagerDuty API format directly.

    Args:
        manage_request: The request model containing the incident IDs and the fields to update
            (status, urgency, assignment, escalation level)

    Returns:
        The updated incidents
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


def add_responders(incident_id: str, request: IncidentResponderRequest) -> IncidentResponderRequestResponse | str:
    """Add responders to an incident.

    Args:
        incident_id: The ID of the incident to add responders to
        request: The responder request data containing user IDs and optional message

    Returns:
        Details of the responder request
    """
    user = ContextResolver.get_user()
    if user is None:
        return "Cannot add responders with account level auth. Please provide a user token."

    payload = request.model_dump()
    payload["requester_id"] = user.id

    response = get_client().rpost(f"/incidents/{incident_id}/responder_requests", json=payload)
    if type(response) is dict and "responder_request" in response:
        # If the response is a dict with a responder_request key, return the model
        return IncidentResponderRequestResponse.model_validate(response["responder_request"])
    return "Unexpected response format: " + str(response)


def list_incident_notes(incident_id: str) -> ListResponseModel[IncidentNote]:
    """List all notes for a specific incident.

    Args:
        incident_id: The ID of the incident to retrieve notes from

    Returns:
        List of IncidentNote objects for the specified incident

    """
    response = get_client().rget(f"/incidents/{incident_id}/notes")

    # The rget method returns the unwrapped data directly (array of notes)
    if isinstance(response, list):
        notes = [IncidentNote.model_validate(note) for note in response]
        return ListResponseModel[IncidentNote](response=notes)

    # Fallback if response format is unexpected
    return ListResponseModel[IncidentNote](response=[])


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


def create_incident_status_update(incident_id: str, message: str) -> str:
    """Create a status update on an incident.

    Posts a status update message to an incident, notifying subscribers and
    stakeholders of the current state. The message appears in the incident
    timeline and is sent to notification subscribers.

    Args:
        incident_id: The ID of the incident to post the status update to
        message: The status update message text

    Returns:
        JSON string of the created status update
    """
    response = get_client().rpost(
        f"/incidents/{incident_id}/status_updates",
        json={"message": message},
    )
    return json.dumps(response)


def get_outlier_incident(
    incident_id: str,
    since: datetime | None = None,
) -> OutlierIncidentResponse:
    """Get Outlier Incident information for a given Incident on its Service.

    Outlier Incident returns incident that deviates from the expected patterns
    for the same Service. This feature is currently available as part of the
    Event Intelligence package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get outlier incident information for
        since: The start of the date range over which you want to search.
            Maximum range is 6 months.

    Returns:
        Outlier incident information calculated over the same Service as the given Incident
    """
    params: dict[str, Any] = {}
    if since:
        params["since"] = since.isoformat()
    response = get_client().rget(f"/incidents/{incident_id}/outlier_incident", params=params)
    return OutlierIncidentResponse.from_api_response(response)


def get_past_incidents(
    incident_id: str,
    limit: int = 5,
    *,
    total: bool = False,
) -> PastIncidentsResponse:
    """Get Past Incidents related to a specific incident ID.

    Past Incidents returns Incidents within the past 6 months that have similar
    metadata and were generated on the same Service as the parent Incident.
    This feature is currently available as part of the Event Intelligence package
    or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get past incidents for
        limit: The number of results to be returned. Default is 5, maximum is 999.
        total: Include the total number of Past Incidents in the response. Default is False.

    Returns:
        List of past incidents with similarity scores
    """
    params: dict[str, Any] = {"limit": limit, "total": total}
    response = get_client().rget(f"/incidents/{incident_id}/past_incidents", params=params)
    return PastIncidentsResponse.from_api_response(response, default_limit=limit)


def get_related_incidents(
    incident_id: str,
    additional_details: list[str] | None = None,
) -> RelatedIncidentsResponse:
    """Get Related Incidents for a specific incident ID.

    Returns the 20 most recent Related Incidents that are impacting other Responders
    and Services. This feature is currently available as part of the Event Intelligence
    package or Digital Operations plan only.

    Args:
        incident_id: The ID of the incident to get related incidents for
        additional_details: Array of additional attributes to include on returned incidents.
            Allowed values are 'incident'.

    Returns:
        List of related incidents and their relationships
    """
    params: dict[str, Any] = {}
    if additional_details:
        params["additional_details[]"] = additional_details
    response = get_client().rget(f"/incidents/{incident_id}/related_incidents", params=params)
    return RelatedIncidentsResponse.from_api_response(response)
