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


class ContactMethod(BaseModel):
    """Contact method for a user."""

    id: str = Field(description="The ID of the contact method")
    type: str = Field(description="The type of contact method (email_contact_method, phone_contact_method, etc.)")
    summary: str | None = Field(default=None, description="A short-form summary of the contact method")
    label: str | None = Field(default=None, description="The label (e.g., 'Work', 'Mobile')")
    address: str | None = Field(default=None, description="The email address (for email contact methods)")
    phone_number: str | None = Field(default=None, description="The phone number (for phone contact methods)")
    country_code: int | None = Field(default=None, description="The country code for phone contact methods")
    enabled: bool | None = Field(default=None, description="Whether this contact method is enabled")
    blacklisted: bool | None = Field(default=None, description="Whether this contact method is blacklisted")
    send_short_email: bool | None = Field(default=None, description="Send short emails for email contact methods")
    send_html_email: bool | None = Field(default=None, description="Send HTML emails for email contact methods")


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
    contact_methods: list[ContactMethod] | None = Field(
        default=None,
        description="The list of contact methods for the user (only populated when requested with include parameter)",
    )

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
    include: list[str] | None = Field(
        description="Array of additional details to include (e.g., 'contact_methods')",
        default=None,
    )

    def to_params(self):
        params = {}
        if self.query:
            params["query"] = self.query
        if self.teams_ids:
            params["teams_ids[]"] = self.teams_ids
        if self.include:
            params["include[]"] = self.include
        if self.limit:
            params["limit"] = self.limit
        return params
