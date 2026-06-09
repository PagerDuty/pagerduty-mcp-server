from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.escalation_policies import EscalationPolicyReference
from pagerduty_mcp.models.references import ScheduleReference, UserReference


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
    service_ids: list[str] | None = Field(
        description="Filter by service IDs. Resolves each service to its escalation policy to find on-call responders.",
        default=None,
    )
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
