from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import (
    ServiceReference,
    TeamReference,
)


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
    id: str | None = None  # ID is read-only in API responses
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


class EscalationPolicyReference(BaseModel):
    id: str = Field(description="The ID of the escalation policy")
    summary: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information"
        " about the escalation policy. Optional for create/update operations.",
    )

    @computed_field
    @property
    def type(self) -> Literal["escalation_policy_reference"]:
        return "escalation_policy_reference"


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
