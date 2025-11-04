from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.escalation_policies import EscalationPolicyReference
from pagerduty_mcp.models.references import TeamReference


class Service(BaseModel):
    id: str | None = Field(description="The ID of the service", default=None)
    name: str | None = Field(default=None, description="The name of the service")
    description: str | None = Field(default=None, description="The description of the service")
    escalation_policy: EscalationPolicyReference
    teams: list[TeamReference] | None = Field(default=None, description="List of teams associated with the service")

    @computed_field
    @property
    def type(self) -> Literal["service"]:
        return "service"


class ServiceQuery(BaseModel):
    query: str | None = Field(
        description="filters the result, showing only the records whose name matches the query", default=None
    )
    teams_ids: list[str] | None = Field(description="Filter incidents by team IDs", default=None)
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
        if self.teams_ids:
            params["teams_ids[]"] = self.teams_ids
        return params


class ServiceCreate(BaseModel):
    service: Service = Field(
        description="The service to create",
    )
