from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT, Relationship
from pagerduty_mcp.models.references import TeamReference


class BusinessService(BaseModel):
    id: str | None = Field(description="The ID of the business service", default=None)
    name: str | None = Field(default=None, description="The name of the business service")
    description: str | None = Field(default=None, description="The description of the business service")
    point_of_contact: str | None = Field(default=None, description="The point of contact for the business service")
    team: TeamReference | None = Field(default=None, description="The team associated with the business service")

    @computed_field
    @property
    def type(self) -> Literal["business_service"]:
        return "business_service"


class BusinessServiceQuery(BaseModel):
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="Pagination limit",
    )

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.limit:
            params["limit"] = self.limit
        return params


class BusinessServiceDependencyList(BaseModel):
    relationships: list[Relationship]
