"""Models for PagerDuty People MCP Server.

This module consolidates models from multiple domains:
- Users
- Teams
- Schedules
- On-calls
- Escalation Policies
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT, RequestScope
from pagerduty_mcp.models.references import (
    ScheduleReference,
    ServiceReference,
    TeamReference,
    UserReference,
)

# =============================================================================
# USER MODELS
# =============================================================================

UserRole = Literal[
    "admin",
    "limited_user",
    "observer",
    "owner",
    "read_only_user",
    "restricted_access",
    "read_only_limited_user",
    "user",
]


class User(BaseModel):
    id: str | None = Field(
        description="The ID of the user",
        default=None,
    )
    summary: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information about the user",
    )
    name: str = Field(description="The name of the user")
    email: str = Field(description="The email of the user")
    role: UserRole = Field(description="The user role in PagerDuty (admin, limited_user, observer, etc.)")
    teams: list[TeamReference] = Field(description="The list of teams to which the user belongs")

    @computed_field
    @property
    def type(self) -> Literal["user"]:
        return "user"


class UserQuery(BaseModel):
    query: str | None = Field(
        description="Filters the result, showing only the records whose name matches the query",
        default=None,
    )
    teams_ids: list[str] | None = Field(description="Filter users by team IDs", default=None)
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self):
        params = {}
        if self.query:
            params["query"] = self.query
        if self.teams_ids:
            params["teams_ids[]"] = self.teams_ids
        if self.limit:
            params["limit"] = self.limit
        return params


# =============================================================================
# TEAM MODELS
# =============================================================================

TeamDefaultRole = Literal["manager", "none"]
TeamMemberRole = Literal["observer", "responder", "manager"]


class Team(BaseModel):
    id: str | None = Field(description="The ID of the team", default=None)
    summary: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information about the team",
    )
    name: str
    description: str | None = None

    @computed_field
    @property
    def type(self) -> Literal["team"]:
        return "team"


class TeamQuery(BaseModel):
    scope: RequestScope | None = Field(
        default="all",
        description="Scope of the query. 'all' for all teams, 'my' for teams the user is a member of",
    )
    query: str | None = Field(
        description="filters the result, showing only the records whose name matches the query", default=None
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.query:
            params["query"] = self.query
        if self.limit:
            params["limit"] = self.limit
        return params


class TeamCreate(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information about the team",
    )
    default_role: TeamDefaultRole | None = Field(
        default="manager",
        description="The default role for new users added to the team",
    )


class TeamCreateRequest(BaseModel):
    team: TeamCreate = Field(
        description="The team to create",
    )


class TeamMemberAdd(BaseModel):
    user_id: str = Field(description="The ID of the user to add to the team", exclude=True)
    role: TeamMemberRole = Field(
        default="manager",
        description="The role of the user in the team",
    )


# =============================================================================
# SCHEDULE MODELS
# =============================================================================


class ScheduleLayerUser(BaseModel):
    user: UserReference = Field(description="The reference to the user in this layer")


class ScheduleLayer(BaseModel):
    id: str = Field(description="The ID of the schedule layer")
    start: datetime = Field(description="The start time of this layer")
    end: datetime | None = Field(
        default=None,
        description="The end time of this layer. If null, the layer does not end",
    )
    name: str = Field(description="The name of the schedule layer")
    rotation_virtual_start: datetime = Field(
        description="The effective start time of the layer. This can be before the start time of the schedule"
    )
    rotation_turn_length_seconds: int = Field(description="The duration of each on-call shift in seconds")
    users: list[ScheduleLayerUser] = Field(
        description="The ordered list of users on this layer. The position of the user on the list"
        " determines their order in the layer"
    )
    restrictions: list[dict[str, Any]] | None = Field(
        default=None,
        description="An array of restrictions for the layer. A restriction is a limit on which"
        " period of the day or week the schedule layer can accept assignments",
    )


class Schedule(BaseModel):
    id: str | None = Field(description="The ID of the schedule", default=None)
    summary: str = Field(
        description="A short-form, server-generated string that provides succinct information about the schedule"
    )
    name: str = Field(description="The name of the schedule")
    description: str | None = Field(default=None, description="The description of the schedule")
    time_zone: str = Field(description="The time zone of the schedule")
    self_url: str | None = Field(default=None, description="The API URL at which this schedule is accessible")
    html_url: str | None = Field(
        default=None,
        description="The URL at which this schedule is accessible in the PagerDuty UI",
    )
    created_at: datetime | None = Field(default=None, description="The date/time when this schedule was created")
    updated_at: datetime | None = Field(default=None, description="The date/time when this schedule was last updated")
    users: list[UserReference] | None = Field(default=None, description="The users associated with this schedule")
    teams: list[TeamReference] | None = Field(default=None, description="The teams associated with this schedule")
    schedule_layers: list[ScheduleLayer] | None = Field(
        default=None, description="A list of schedule layers for this schedule"
    )

    @computed_field
    @property
    def type(self) -> Literal["schedule"]:
        return "schedule"


class ScheduleQuery(BaseModel):
    query: str | None = Field(description="Filter schedules by name or description", default=None)
    team_ids: list[str] | None = Field(description="Filter schedules by team IDs", default=None)
    user_ids: list[str] | None = Field(description="Filter schedules by user IDs", default=None)
    include: list[str] | None = Field(
        description="Include additional details in response, such as 'schedule_layers'",
        default=None,
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.query:
            params["query"] = self.query
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.user_ids:
            params["user_ids[]"] = self.user_ids
        if self.include:
            params["include[]"] = self.include
        if self.limit:
            params["limit"] = self.limit
        return params


class Override(BaseModel):
    start: datetime = Field(description="The start time of the override")
    end: datetime = Field(description="The end time of the override")
    user: UserReference = Field(description="The user for the override")


class ScheduleOverrideCreate(BaseModel):
    overrides: list[Override] = Field(description="The list of overrides to create for the schedule")


# =============================================================================
# ON-CALL MODELS
# =============================================================================


class EscalationPolicyReference(BaseModel):
    id: str = Field(description="The ID of the escalation policy")
    summary: str = Field(
        description="A short-form, server-generated string that provides succinct information"
        " about the escalation policy"
    )

    @computed_field
    @property
    def type(self) -> Literal["escalation_policy_reference"]:
        return "escalation_policy_reference"


class Oncall(BaseModel):
    escalation_policy: EscalationPolicyReference | None = Field(
        default=None, description="The escalation policy associated with the on-call"
    )
    escalation_level: int | None = Field(default=None, description="The escalation level for the on-call")
    schedule: ScheduleReference | None = Field(default=None, description="The schedule associated with the on-call")
    user: UserReference = Field(description="The user who is on-call")
    start: datetime | None = Field(
        default=None, description="The start of the on-call. If null, the on-call is a permanent user on-call"
    )
    end: datetime | None = Field(
        default=None, description="The end of the on-call. If null, the user does not go off-call"
    )


class OncallQuery(BaseModel):
    time_zone: str | None = Field(
        description="Time zone in which dates should be rendered (e.g., 'America/New_York')", default=None
    )
    user_ids: list[str] | None = Field(description="Filter by user IDs", default=None)
    escalation_policy_ids: list[str] | None = Field(description="Filter by escalation policy IDs", default=None)
    schedule_ids: list[str] | None = Field(description="Filter by schedule IDs", default=None)
    since: datetime | None = Field(description="Start of timerange - defaults to current time", default=None)
    until: datetime | None = Field(description="End of timerange - defaults to current time", default=None)
    earliest: bool | None = Field(
        description="Return only the earliest oncall for each combination of user and escalation policy",
        default=True,
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.time_zone:
            params["time_zone"] = self.time_zone
        if self.user_ids:
            params["user_ids[]"] = self.user_ids
        if self.escalation_policy_ids:
            params["escalation_policy_ids[]"] = self.escalation_policy_ids
        if self.schedule_ids:
            params["schedule_ids[]"] = self.schedule_ids
        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.earliest is not None:
            params["earliest"] = str(self.earliest).lower()
        if self.limit:
            params["limit"] = self.limit
        return params


# =============================================================================
# ESCALATION POLICY MODELS
# =============================================================================


class EscalationTarget(BaseModel):
    id: str = Field(description="The ID of the escalation target (user or schedule)")
    type: Literal["user_reference", "schedule_reference"] = Field(
        description="The type of target - either a user or a schedule reference"
    )
    summary: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information about the target",
    )


class EscalationRule(BaseModel):
    id: str | None = None
    escalation_delay_in_minutes: int = Field(
        description="The number of minutes before an unacknowledged incident escalates away from this rule."
    )
    targets: list[EscalationTarget] = Field(
        description="The targets an incident should be assigned to upon reaching this rule."
    )
    escalation_rule_assignment_strategy: Literal["round_robin", "assign_to_everyone"] | None = Field(
        description="The strategy used to assign the escalation rule to an incident.",
        default=None,
    )


class EscalationPolicy(BaseModel):
    id: str = Field(description="The ID of the escalation policy")
    summary: str = Field(
        description="A short-form, server-generated string that provides succinct information"
        " about the escalation policy"
    )
    name: str = Field(description="The name of the escalation policy")
    description: str | None = Field(default=None, description="The description of the escalation policy")
    escalation_rules: list[EscalationRule] = Field(description="The ordered list of escalation rules for the policy")
    num_loops: int = Field(
        default=0,
        description="The number of times the escalation policy will repeat after reaching the end of its escalation",
    )
    on_call_handoff_notifications: Literal["if_has_services", "always"] | None = Field(
        description="Determines how on call handoff notifications will be sent for users on theescalation policy",
        default="if_has_services",
    )
    self_url: str | None = Field(default=None, description="The API URL at which this escalation policy is accessible")
    html_url: str | None = Field(
        default=None, description="The URL at which this escalation policy is accessible in the PagerDuty UI"
    )
    services: list[ServiceReference] | None = Field(
        default=None, description="The services that are using this escalation policy"
    )
    teams: list[TeamReference] | None = Field(
        default=None, description="The teams associated with this escalation policy"
    )
    created_at: datetime | None = Field(
        default=None, description="The date/time when this escalation policy was created"
    )
    updated_at: datetime | None = Field(
        default=None, description="The date/time when this escalation policy was last updated"
    )

    @computed_field
    @property
    def type(self) -> Literal["escalation_policy"]:
        return "escalation_policy"


class EscalationPolicyQuery(BaseModel):
    query: str | None = Field(description="Filter escalation policies by name or description", default=None)
    user_ids: list[str] | None = Field(description="Filter escalation policies by user IDs", default=None)
    team_ids: list[str] | None = Field(description="Filter escalation policies by team IDs", default=None)
    include: list[str] | None = Field(
        description="Include additional details in response, such as 'services' or 'teams'",
        default=None,
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.query:
            params["query"] = self.query
        if self.user_ids:
            params["user_ids[]"] = self.user_ids
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.include:
            params["include[]"] = self.include
        if self.limit:
            params["limit"] = self.limit
        return params
