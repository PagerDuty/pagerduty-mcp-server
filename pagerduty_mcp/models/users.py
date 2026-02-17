from typing import Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import TeamReference

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
            params["team_ids[]"] = self.teams_ids
        if self.limit:
            params["limit"] = self.limit
        return params
