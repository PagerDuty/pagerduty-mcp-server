from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import (
    DEFAULT_PAGINATION_LIMIT,
    MAXIMUM_PAGINATION_LIMIT,
    RequestScope,
)

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
