from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

StatusPageType = Literal["public", "private"]
PostType = Literal["incident", "maintenance"]


class StatusPageReference(BaseModel):
    id: str = Field(description="Status page unique identifier")
    type: Literal["status_page"] = Field(default="status_page")


class StatusPage(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope")
    name: str = Field(description="The name of a Status Page")
    published_at: datetime | None = Field(
        default=None, description="The date time moment when a Status Page was published"
    )
    status_page_type: StatusPageType = Field(description="The type of Status Pages")
    url: str = Field(description="The URL from which the Status Page can be accessed")
    type: Literal["status_page"] = Field(default="status_page")


class StatusPageSeverity(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope")
    self: str = Field(description="The API resource URL of the Severity")
    description: str = Field(description="Human-readable text that describes the Severity level")
    post_type: PostType = Field(description="The type of the Post")
    status_page: StatusPageReference
    type: Literal["status_page_severity"] = Field(default="status_page_severity")


class StatusPageImpact(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope")
    self: str = Field(description="The API resource URL of the Impact")
    description: str = Field(description="Human-readable text that describes the Impact level")
    post_type: PostType = Field(description="The type of the Post")
    status_page: StatusPageReference
    type: Literal["status_page_impact"] = Field(default="status_page_impact")


class StatusPageStatus(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope")
    self: str = Field(description="The API resource URL of the Status")
    description: str = Field(description="Human-readable text that describes the Status")
    post_type: PostType = Field(description="The type of the Post")
    status_page: StatusPageReference
    type: Literal["status_page_status"] = Field(default="status_page_status")


class StatusPagePostReference(BaseModel):
    id: str = Field(description="Status page post unique identifier")
    self: str | None = Field(default=None, description="The API resource URL")
    type: Literal["status_page_post"] = Field(default="status_page_post")


class StatusPageSeverityReference(BaseModel):
    id: str = Field(description="Status page severity unique identifier")
    self: str | None = Field(default=None, description="The API resource URL")
    type: Literal["status_page_severity"] = Field(default="status_page_severity")


class StatusPageImpactReference(BaseModel):
    id: str = Field(description="Status page impact unique identifier")
    self: str | None = Field(default=None, description="The API resource URL")
    type: Literal["status_page_impact"] = Field(default="status_page_impact")


class StatusPageStatusReference(BaseModel):
    id: str = Field(description="Status page status unique identifier")
    self: str | None = Field(default=None, description="The API resource URL")
    type: Literal["status_page_status"] = Field(default="status_page_status")


class StatusPageServiceReference(BaseModel):
    id: str = Field(description="Status page service unique identifier")
    self: str | None = Field(default=None, description="The API resource URL")
    type: Literal["status_page_service"] = Field(default="status_page_service")


class StatusPagePostmortemReference(BaseModel):
    id: str = Field(description="Status page postmortem unique identifier")
    self: str = Field(description="The API resource URL")
    type: Literal["status_page_postmortem"] = Field(default="status_page_postmortem")


class StatusPagePostUpdateReference(BaseModel):
    id: str = Field(description="Status page post update unique identifier")
    self: str | None = Field(default=None, description="The API resource URL")
    type: Literal["status_page_post_update"] = Field(default="status_page_post_update")


class ImpactedService(BaseModel):
    impact: StatusPageImpactReference
    service: StatusPageServiceReference


class StatusPagePostUpdate(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope")
    self: str = Field(description="The API resource URL of the Post Update")
    message: str = Field(description="The message content of the Post Update")
    notify_subscribers: bool = Field(
        default=False, description="Whether to notify subscribers of this update"
    )
    post: StatusPagePostReference
    reported_at: datetime = Field(description="The date and time the Post Update was reported")
    reviewed_status: str | None = Field(default=None, description="The review status of the update")
    severity: StatusPageSeverityReference
    status: StatusPageStatusReference
    impacted_services: list[ImpactedService] | None = Field(
        default=None, description="List of impacted services"
    )
    type: Literal["status_page_post_update"] = Field(default="status_page_post_update")


class StatusPagePost(BaseModel):
    id: str = Field(description="An unique identifier within Status Page scope")
    self: str = Field(description="The API resource URL of the Post")
    title: str = Field(description="The title given to a Post")
    post_type: PostType = Field(description="The type of the Post")
    starts_at: datetime | None = Field(
        default=None, description="The date and time the Post intent becomes effective"
    )
    ends_at: datetime | None = Field(
        default=None, description="The date and time the Post intent is concluded"
    )
    status_page: StatusPageReference
    postmortem: StatusPagePostmortemReference | None = Field(
        default=None, description="The postmortem associated with the post"
    )
    updates: list[StatusPagePostUpdateReference] | None = Field(
        default=None, description="List of updates associated with the post"
    )
    type: Literal["status_page_post"] = Field(default="status_page_post")

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "StatusPagePost":
        """Create StatusPagePost from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Wrapped: {"post": {...}}
        - Direct: {...} (post data directly)
        """
        if "post" in response_data:
            return cls.model_validate(response_data["post"])
        return cls.model_validate(response_data)


class StatusPagePostUpdateRequest(BaseModel):
    message: str = Field(description="The message content of the Post Update")
    severity: StatusPageSeverityReference = Field(description="The severity of the update")
    status: StatusPageStatusReference = Field(description="The status of the update")
    impacted_services: list[ImpactedService] | None = Field(
        default=None, description="List of impacted services"
    )
    notify_subscribers: bool = Field(
        default=False, description="Whether to notify subscribers of this update"
    )
    type: Literal["status_page_post_update"] = Field(default="status_page_post_update")


class StatusPagePostUpdateRequestBody(BaseModel):
    post_update: StatusPagePostUpdateRequest


class StatusPagePostCreate(BaseModel):
    type: Literal["status_page_post"] = Field(default="status_page_post")
    title: str = Field(description="The title given to a Post", min_length=1, max_length=128)
    post_type: PostType = Field(description="The type of the Post")
    starts_at: datetime | None = Field(
        default=None, description="The date and time the Post intent becomes effective"
    )
    ends_at: datetime | None = Field(
        default=None, description="The date and time the Post intent is concluded"
    )
    updates: list[StatusPagePostUpdateRequest] | None = Field(
        default=None, description="Post Updates to be associated with a Post"
    )


class StatusPagePostCreateRequest(BaseModel):
    post: StatusPagePostCreate


class StatusPageQuery(BaseModel):
    status_page_type: StatusPageType | None = Field(default=None, description="The type of Status Page")

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.status_page_type:
            params["status_page_type"] = self.status_page_type
        return params


class StatusPageSeverityQuery(BaseModel):
    post_type: PostType | None = Field(default=None, description="Filter by Post type")

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.post_type:
            params["post_type"] = self.post_type
        return params


class StatusPageImpactQuery(BaseModel):
    post_type: PostType | None = Field(default=None, description="Filter by Post type")

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.post_type:
            params["post_type"] = self.post_type
        return params


class StatusPageStatusQuery(BaseModel):
    post_type: PostType | None = Field(default=None, description="Filter by Post type")

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.post_type:
            params["post_type"] = self.post_type
        return params
