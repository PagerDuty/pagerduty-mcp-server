from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.references import ServiceReference, UserReference

IncidentStatus = Literal["triggered", "acknowledged", "resolved"]

IncidentManageStatus = Literal["acknowledged", "resolved"]

IncidentUrgency = Literal[
    "high",
    "low",
]
IncidentManageRequestType = Literal["change_status", "reassign", "escalate", "change_urgency"]

Urgency = Literal["high", "low"]
IncidentRequestScope = Literal["all", "teams", "assigned"]


class IncidentQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: list[IncidentStatus] | None = Field(description="filter incidents by status", default=None)
    since: datetime | None = Field(description="filter incidents since a specific date", default=None)
    until: datetime | None = Field(description="filter incidents until a specific date", default=None)
    user_ids: list[str] | None = Field(description="Filter incidents by user IDs", default=None)
    service_ids: list[str] | None = Field(description="Filter incidents by service IDs", default=None)
    teams_ids: list[str] | None = Field(description="Filter incidents by team IDs", default=None)
    urgencies: list[Urgency] | None = Field(description="Filter incidents by urgency", default=None)
    request_scope: IncidentRequestScope = Field(
        description="Filter incidents by request . Either all, my teams or assigned to me",
        default="all",
    )
    limit: int | None = Field(
        ge=1,
        le=MAX_RESULTS,
        default=MAX_RESULTS,
        description="Maximum number of results to return. The maximum is 1000",
    )
    sort_by: (
        list[
            Literal[
                "incident_number:asc",
                "incident_number:desc",
                "created_at:asc",
                "created_at:desc",
                "resolved_at:asc",
                "resolved_at:desc",
                "urgency:asc",
                "urgency:desc",
            ]
        ]
        | None
    ) = Field(
        default=None,
        description=(
            "Used to specify both the field you wish to sort the results on "
            "(incident_number/created_at/resolved_at/urgency), as well as the direction (asc/desc) of the results. "
            "The sort_by field and direction should be separated by a colon. A maximum of two fields can be included, "
            "separated by a comma. Sort direction defaults to ascending. The account must have the urgencies ability "
            "to sort by the urgency."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def _reject_statuses_param(cls, data: Any):
        # Provide a helpful error when a user mistakenly passes 'statuses' instead of 'status'
        if isinstance(data, dict) and "statuses" in data:
            raise ValueError(
                'The correct parameter to filter by multiple Incidents statuses is "status", not "statuses",'
                " please correct your input and try again"
            )
        return data

    # TODO: Create parent class and generalize the to_params method
    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.status:
            params["statuses[]"] = self.status
        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.service_ids:
            params["service_ids[]"] = self.service_ids
        if self.teams_ids:
            params["teams_ids[]"] = self.teams_ids
        if self.user_ids:
            params["user_ids[]"] = self.user_ids
        if self.urgencies:
            params["urgencies[]"] = self.urgencies
        if self.sort_by:
            params["sort_by"] = ",".join(self.sort_by)
        return params


class OutlierIncidentQuery(BaseModel):
    """Query model for retrieving outlier incident information."""

    model_config = ConfigDict(extra="forbid")

    since: datetime | None = Field(
        default=None,
        description="The start of the date range over which you want to search. Maximum range is 6 months.",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.since:
            params["since"] = self.since.isoformat()
        return params


class PastIncidentsQuery(BaseModel):
    """Query model for retrieving past incidents related to a specific incident."""

    model_config = ConfigDict(extra="forbid")

    limit: int | None = Field(
        default=None,
        ge=1,
        le=999,
        description="The number of results to be returned in the response. Default is 5, maximum is 999.",
    )
    total: bool | None = Field(
        default=None,
        description="Set to true to include the total number of Past Incidents in the response",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.limit is not None:
            params["limit"] = self.limit
        if self.total is not None:
            params["total"] = self.total
        return params


class RelatedIncidentsQuery(BaseModel):
    """Query model for retrieving related incidents for a specific incident."""

    model_config = ConfigDict(extra="forbid")

    additional_details: list[str] | None = Field(
        default=None,
        description="Array of additional attributes to any of the returned incidents for related incidents. "
         "Allowed values are 'incident'",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.additional_details:
            params["additional_details[]"] = self.additional_details
        return params


# TODO: This should be moved to its own file
class Assignment(BaseModel):
    at: datetime = Field(description="Time at which the assignment was created.")
    assignee: UserReference = Field(description="The user assigned to the incident")


class Incident(BaseModel):
    id: str | None = Field(description="The ID of the incident", default=None)
    summary: str | None = Field(default=None, description="A short summary of the incident")
    incident_number: int = Field(description="The number of the incident. This is unique across your account")
    status: IncidentStatus = Field(description="The current status of the incident")
    title: str = Field(description="A succinct description of the nature, symptoms, cause, or effect of the incident")
    created_at: datetime = Field(description="The time the incident was first triggered")
    updated_at: datetime = Field(description="The time the incident was last modified")
    resolved_at: datetime | None = Field(
        default=None,
        description="The time the incident became resolved or null if the incident is not resolved",
    )
    service: ServiceReference = Field(description="The service the incident is on")
    assignments: list[Assignment] | None = Field(
        default=None,
        description="The users assigned to the incident",
    )

    @computed_field
    @property
    def type(self) -> Literal["incident"]:
        return "incident"


class IncidentBody(BaseModel):
    details: str = Field(description="The details of the incident body")

    @computed_field
    @property
    def type(self) -> Literal["incident_body"]:
        return "incident_body"


class IncidentCreate(BaseModel):
    title: str = Field(description="The title of the incident")
    service: ServiceReference = Field(description="The service associated with the incident")
    urgency: Urgency | None = Field(description="The urgency of the incident", default="high")
    body: IncidentBody | None = Field(
        default=None,
        description="The body of the incident. This is a free-form text field that can be used to "
        "provide additional details about the incident.",
    )

    @computed_field
    @property
    def type(self) -> Literal["incident"]:
        return "incident"


class IncidentCreateRequest(BaseModel):
    incident: IncidentCreate = Field(description="The incident to create")


class IncidentManageRequest(BaseModel):
    incident_ids: list[str] = Field(description="The ID of the incidents to manage")
    assignement: UserReference | None = Field(
        default=None,
        description="The user to assign the incident to",
    )
    status: IncidentManageStatus | None = Field(
        default=None,
        description="The status to set the incident to",
    )
    urgency: IncidentUrgency | None = Field(
        default=None,
        description="The priority to set the incident to",
    )
    escalation_level: int | None = Field(
        default=None,
        description="The escalation level to set the incident to",
    )


class ResponderRequest(BaseModel):
    id: str = Field(description="The ID of the user or escalation policy to request as a responder")
    type: Literal["user_reference", "escalation_policy_reference"] = Field(
        description="The type of target (either a user or an escalation policy)"
    )


class ResponderRequestTarget(BaseModel):
    responder_request_target: ResponderRequest = Field(
        description="Array of user or escalation policy IDs to request as responders",
    )


class IncidentResponderRequest(BaseModel):
    requester_id: str | None = Field(description="User ID of the requester")
    message: str = Field(
        description="Optional message to include with the responder request",
    )
    responder_request_targets: list[ResponderRequestTarget] = Field(
        description="Array of user or escalation policy IDs to request as responders",
    )


class IncidentResponderRequestResponse(BaseModel):
    requester: UserReference = Field(description="The user who requested the responders")
    requested_at: datetime = Field(description="When the request was made")
    message: str | None = Field(default=None, description="The message included with the request")
    responder_request_targets: list[dict[str, Any]] = Field(description="The users requested to respond")


class IncidentNote(BaseModel):
    id: str | None = Field(description="The ID of the note", default=None)
    content: str = Field(description="The content of the note")
    created_at: datetime = Field(description="The time the note was created")
    user: UserReference = Field(description="The user who created the note")


class Occurrence(BaseModel):
    """Occurrence information for an outlier incident."""
    count: int = Field(description="The number of times this incident pattern has occurred")
    frequency: float = Field(description="The frequency of occurrence")
    category: str = Field(description="The category of occurrence (e.g., 'rare')")
    since: datetime = Field(description="The start of the occurrence time range")
    until: datetime = Field(description="The end of the occurrence time range")


class OutlierIncidentReference(BaseModel):
    """Minimal incident reference returned by the outlier incident endpoint."""
    id: str = Field(description="The globally unique identifier of the incident")
    created_at: datetime = Field(description="The date/time the incident was first triggered")
    self: str = Field(description="The URL at which the object is accessible")
    title: str | None = Field(default=None,
                              description="The description of the nature, symptoms, cause, "
                              "or effect of the incident")
    occurrence: Occurrence = Field(description="Occurrence information for this outlier incident")


class IncidentTemplate(BaseModel):
    """Template information for an outlier incident."""
    id: str = Field(description="The ID of the incident template")
    cluster_id: str = Field(description="The cluster ID")
    mined_text: str = Field(description="The mined text pattern for this incident template")


class OutlierIncident(BaseModel):
    incident: OutlierIncidentReference = Field(description="The outlier incident details")
    incident_template: IncidentTemplate = Field(description="The incident template information")


class OutlierIncidentResponse(BaseModel):
    outlier_incident: OutlierIncident = Field(description="Outlier incident information")

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any] | list) -> "OutlierIncidentResponse":
        """Create OutlierIncidentResponse from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Wrapped: {"outlier_incident": {...}}
        - Direct: {...} (outlier incident data directly)
        - Edge case: [] (empty list, treated as error)

        Args:
            response_data: The API response data

        Returns:
            OutlierIncidentResponse instance

        Raises:
            ValueError: If response is an empty list or invalid format
        """
        # Handle edge case: empty list
        if isinstance(response_data, list) and len(response_data) == 0:
            raise ValueError("Empty response from outlier incident endpoint")

        # Handle wrapped format: {"outlier_incident": {...}}
        if isinstance(response_data, dict) and "outlier_incident" in response_data:
            return cls.model_validate(response_data)

        # Handle direct format: {...} (outlier incident data directly)
        if isinstance(response_data, dict):
            return cls(outlier_incident=OutlierIncident.model_validate(response_data))

        raise ValueError(f"Unexpected response format: {type(response_data)}")


class PastIncidentReference(BaseModel):
    id: str = Field(description="The globally unique identifier of the incident")
    created_at: datetime = Field(description="The date/time the incident was first triggered")
    self: str = Field(description="The URL at which the object is accessible")
    title: str = Field(description="The description of the nature, symptoms, cause, or effect of the incident")


class PastIncident(BaseModel):
    incident: PastIncidentReference = Field(description="Past incident reference")
    score: float = Field(description="The computed similarity score associated with the incident and parent incident")


class PastIncidentsResponse(BaseModel):
    past_incidents: list[PastIncident] = Field(description="List of past incidents")
    total: int | None = Field(
        default=None, description="The total number of Past Incidents if the total parameter was set"
    )
    limit: int = Field(description="The maximum number of Incidents requested")

    @classmethod
    def from_api_response(
        cls, response_data: dict[str, Any] | list, default_limit: int = 5
    ) -> "PastIncidentsResponse":
        """Create PastIncidentsResponse from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Standard dict: {"past_incidents": [...], "limit": 5, "total": 10}
        - Edge case: [] (empty list, returns default structure)

        Args:
            response_data: The API response data
            default_limit: The default limit to use if not present in response (default: 5)

        Returns:
            PastIncidentsResponse instance
        """
        # Handle edge case: empty list
        if isinstance(response_data, list) and len(response_data) == 0:
            return cls(past_incidents=[], limit=default_limit, total=0)

        # Handle normal dict response
        if isinstance(response_data, dict):
            return cls.model_validate(response_data)

        raise ValueError(f"Unexpected response format: {type(response_data)}")


class Relationship(BaseModel):
    """Relationship information for a related incident."""
    type: str = Field(description="The type of relationship (e.g., 'machine_learning_inferred', 'service_dependency')")
    metadata: dict[str, Any] = Field(description="Metadata about the relationship, structure varies by type")


class RelatedIncident(BaseModel):
    incident: PastIncidentReference = Field(description="The related incident reference")
    relationships: list[Relationship] = Field(description="List of relationships to the parent incident")


class RelatedIncidentsResponse(BaseModel):
    related_incidents: list[RelatedIncident] = Field(description="List of related incidents")

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any] | list) -> "RelatedIncidentsResponse":
        """Create RelatedIncidentsResponse from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Standard dict: {"related_incidents": [...]}
        - Edge case: [] (empty list, returns default structure)

        Args:
            response_data: The API response data

        Returns:
            RelatedIncidentsResponse instance
        """
        # Handle edge case: empty list
        if isinstance(response_data, list) and len(response_data) == 0:
            return cls(related_incidents=[])

        # Handle normal dict response
        if isinstance(response_data, dict):
            return cls.model_validate(response_data)

        raise ValueError(f"Unexpected response format: {type(response_data)}")
