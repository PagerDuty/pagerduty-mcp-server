from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT


class StatusPageReference(BaseModel):
    id: str = Field(description="Status page unique identifier")
    type: str | None = Field(default="status_page", description="A string that determines the schema of the object")


class StatusPage(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope that defines a Status Page entry")
    name: str = Field(description="The name of a Status Page to be presented as a brand title")
    published_at: datetime | None = Field(
        default=None, description="The date time moment when a Status Page was published to be publicly available"
    )
    status_page_type: Literal["public", "private", "audience_specific"] = Field(
        description=(
            "The type of Status Pages - public is accessible to everyone, "
            "private requiring authentication, or audience_specific for targeted audiences"
        )
    )
    url: str = Field(description="The URL from which the Status Page can be accessed on the internet")

    @computed_field
    @property
    def type(self) -> Literal["status_page"]:
        return "status_page"


class StatusPageQuery(BaseModel):
    status_page_type: Literal["public", "private", "audience_specific"] | None = Field(
        default=None, description="Filter by the type of the Status Page"
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Maximum number of results to return",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.status_page_type:
            params["status_page_type"] = self.status_page_type
        if self.limit:
            params["limit"] = self.limit
        return params


class StatusPageSeverity(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope that defines a Severity entry")
    self_: str | None = Field(default=None, alias="self", description="The API resource URL of the Severity")
    description: str = Field(description="The description is a human-readable text that describes the Severity level")
    post_type: Literal["incident", "maintenance"] = Field(description="The type of the Post")
    status_page: StatusPageReference = Field(description="Status Page reference")

    @computed_field
    @property
    def type(self) -> Literal["status_page_severity"]:
        return "status_page_severity"


class StatusPageSeverityQuery(BaseModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Filter by Post type")
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Maximum number of results to return",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.post_type:
            params["post_type"] = self.post_type
        if self.limit:
            params["limit"] = self.limit
        return params


class StatusPageImpact(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope that defines a Impact entry")
    self_: str | None = Field(default=None, alias="self", description="The API resource URL of the Impact")
    description: str = Field(description="The description is a human-readable text that describes the Impact level")
    post_type: Literal["incident", "maintenance"] = Field(description="The type of the Post")
    status_page: StatusPageReference = Field(description="Status Page reference")

    @computed_field
    @property
    def type(self) -> Literal["status_page_impact"]:
        return "status_page_impact"


class StatusPageImpactQuery(BaseModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Filter by Post type")
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Maximum number of results to return",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.post_type:
            params["post_type"] = self.post_type
        if self.limit:
            params["limit"] = self.limit
        return params


class StatusPageStatus(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope that defines a Status entry")
    self_: str | None = Field(default=None, alias="self", description="The API resource URL of the Status")
    description: str = Field(description="The description is a human-readable text that describes the Status level")
    post_type: Literal["incident", "maintenance"] = Field(description="The type of the Post")
    status_page: StatusPageReference = Field(description="Status Page reference")

    @computed_field
    @property
    def type(self) -> Literal["status_page_status"]:
        return "status_page_status"


class StatusPageStatusQuery(BaseModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Filter by Post type")
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Maximum number of results to return",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.post_type:
            params["post_type"] = self.post_type
        if self.limit:
            params["limit"] = self.limit
        return params


class StatusPagePostReference(BaseModel):
    id: str = Field(description="Status page post unique identifier")
    type: str | None = Field(
        default="status_page_post", description="A string that determines the schema of the object"
    )


class StatusPageStatusReference(BaseModel):
    id: str = Field(description="Status page Status unique identifier")
    type: str | None = Field(
        default="status_page_status", description="A string that determines the schema of the object"
    )


class StatusPageSeverityReference(BaseModel):
    id: str = Field(description="Status page Severity unique identifier")
    type: str | None = Field(
        default="status_page_severity", description="A string that determines the schema of the object"
    )


class StatusPageImpactReference(BaseModel):
    id: str = Field(description="Status page Impact unique identifier")
    type: str | None = Field(
        default="status_page_impact", description="A string that determines the schema of the object"
    )


class StatusPageServiceReference(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope that defines a Service entry")
    type: str | None = Field(default="status_page_service", description="The type of the object returned by the API")


class StatusPagePostUpdateImpact(BaseModel):
    service: StatusPageServiceReference = Field(description="Status Page Service reference")
    impact: StatusPageImpactReference = Field(description="Status Page Impact reference")


class StatusPagePostUpdate(BaseModel):
    id: str | None = Field(default=None, description="The ID of the Post Update")
    self_: str | None = Field(
        default=None, alias="self", description="The path to which the Post Update resource is accessible"
    )
    post: StatusPagePostReference | None = Field(default=None, description="Status Page Post reference")
    message: str | None = Field(default=None, description="The message of the Post Update")
    reviewed_status: Literal["approved", "not_reviewed"] | None = Field(
        default=None, description="The status of the Post Updates to retrieve"
    )
    status: StatusPageStatusReference | None = Field(default=None, description="Status Page Status reference")
    severity: StatusPageSeverityReference | None = Field(default=None, description="Status Page Severity reference")
    impacted_services: list[StatusPagePostUpdateImpact] | None = Field(
        default=None, description="Impacted services represent the status page services affected by a post update"
    )
    update_frequency_ms: int | None = Field(
        default=None, description="The frequency of the next Post Update in milliseconds"
    )
    notify_subscribers: bool | None = Field(
        default=None, description="Determines if the subscribers should be notified of the Post Update"
    )
    reported_at: datetime | None = Field(default=None, description="The date and time the Post Update was reported")

    @computed_field
    @property
    def type(self) -> Literal["status_page_post_update"]:
        return "status_page_post_update"

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "StatusPagePostUpdate":
        """Handle both wrapped and unwrapped API responses."""
        if "post_update" in response_data:
            return cls.model_validate(response_data["post_update"])
        return cls.model_validate(response_data)


class LinkedResourceReference(BaseModel):
    id: str = Field(description="Linked resource unique identifier")
    type: str = Field(description="A string that determines the schema of the object")


class PostmortemReference(BaseModel):
    id: str = Field(description="Postmortem unique identifier")
    type: str = Field(description="A string that determines the schema of the object")


class StatusPagePost(BaseModel):
    id: str | None = Field(
        default=None,
        description="An unique identifier within Status Page scope that defines a single Post resource",
    )
    self_: str | None = Field(default=None, alias="self", description="The API resource URL of the Post")
    post_type: Literal["incident", "maintenance"] = Field(description="The type of the Post")
    status_page: StatusPageReference = Field(description="Status Page reference")
    linked_resource: LinkedResourceReference | None = Field(default=None, description="Linked resource reference")
    postmortem: PostmortemReference | None = Field(default=None, description="Postmortem reference")
    title: str = Field(description="The title given to a Post")
    starts_at: datetime | None = Field(
        default=None, description="The date and time the Post intent becomes effective - only for maintenance post type"
    )
    ends_at: datetime | None = Field(
        default=None, description="The date and time the Post intent is concluded - only for maintenance post type"
    )
    updates: list[StatusPagePostUpdate] | None = Field(
        default=None, description="List of status_page_post_update references associated to a Post"
    )

    @computed_field
    @property
    def type(self) -> Literal["status_page_post"]:
        return "status_page_post"

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "StatusPagePost":
        """Handle both wrapped and unwrapped API responses."""
        if "post" in response_data:
            return cls.model_validate(response_data["post"])
        return cls.model_validate(response_data)


class StatusPagePostUpdateRequest(BaseModel):
    message: str = Field(description="The message of the Post Update")
    status: StatusPageStatusReference = Field(description="Status Page Status reference (required when creating posts)")
    severity: StatusPageSeverityReference = Field(
        description="Status Page Severity reference (required when creating posts)"
    )
    impacted_services: list[StatusPagePostUpdateImpact] = Field(
        default_factory=list,
        description=(
            "Impacted services represent the status page services affected by a post update. "
            "Can be empty list if no services are impacted."
        ),
    )
    update_frequency_ms: int | None = Field(
        default=None, description="The frequency of the next Post Update in milliseconds. Use null for no frequency."
    )
    notify_subscribers: bool = Field(
        default=False, description="Determines if the subscribers should be notified of the Post Update"
    )
    reported_at: datetime | None = Field(default=None, description="The date and time the Post Update was reported")
    post: StatusPagePostReference | None = Field(default=None, description="Status Page Post reference")

    @computed_field
    @property
    def type(self) -> Literal["status_page_post_update"]:
        return "status_page_post_update"


class StatusPagePostUpdateRequestWrapper(BaseModel):
    post_update: StatusPagePostUpdateRequest = Field(description="The post update to create")


class StatusPagePostCreateRequest(BaseModel):
    title: str = Field(description="The title given to a Post")
    post_type: Literal["incident", "maintenance"] = Field(description="The type of the Post")
    starts_at: datetime = Field(
        description=(
            "The date and time the Post intent becomes effective (required for both incident and maintenance posts)"
        )
    )
    ends_at: datetime = Field(
        description="The date and time the Post intent is concluded (required for both incident and maintenance posts)"
    )
    updates: list[StatusPagePostUpdateRequest] = Field(
        description=(
            "Post Updates to be associated with a Post. At least one update is required when creating a post."
        ),
    )
    status_page: StatusPageReference = Field(description="Status Page reference")

    @computed_field
    @property
    def type(self) -> Literal["status_page_post"]:
        return "status_page_post"


class StatusPagePostCreateRequestWrapper(BaseModel):
    post: StatusPagePostCreateRequest = Field(description="The post to create")


class StatusPagePostQuery(BaseModel):
    include: list[Literal["status_page_post_update"]] | None = Field(
        default=None, description="Array of additional Models to include in response"
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.include:
            params["include[]"] = self.include
        return params


class StatusPagePostUpdateQuery(BaseModel):
    reviewed_status: Literal["approved", "not_reviewed"] | None = Field(
        default=None, description="Filter by the reviewed status of the Post Update to retrieve"
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Maximum number of results to return",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.reviewed_status:
            params["reviewed_status"] = self.reviewed_status
        if self.limit:
            params["limit"] = self.limit
        return params
