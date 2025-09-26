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
