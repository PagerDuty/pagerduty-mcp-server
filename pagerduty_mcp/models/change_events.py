from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import IntegrationReference, ServiceReference


class ChangeEvent(BaseModel):
    """Represents a PagerDuty Change Event.

    Change Events represent changes to systems, services, and applications that
    can be correlated with incidents to provide context for troubleshooting.
    """

    id: str | None = Field(default=None, description="The unique identifier of the change event")
    summary: str = Field(description="A brief text summary of the event (maximum 1024 characters)")
    timestamp: datetime | None = Field(
        default=None,
        description="The date and time when the change event occurred (read-only)",
    )
    services: list[ServiceReference] | None = Field(
        default=None,
        description="An array of references to services associated with this change event (read-only)",
    )
    integration: IntegrationReference | None = Field(
        default=None,
        description="Reference to the integration that created this change event (read-only)",
    )
    routing_key: str | None = Field(
        default=None,
        description="The 32-character integration key used for routing the event (read-only)",
    )
    source: str | None = Field(
        default=None,
        description="The unique location of the affected system (read-only)",
    )
    links: list[dict] | None = Field(
        default=None,
        description="List of links with 'href' and 'text' properties for additional context (read-only)",
    )
    images: list[dict] | None = Field(
        default=None,
        description="List of images with 'src', 'href', and 'alt' properties for visual context (read-only)",
    )
    custom_details: dict | None = Field(
        default=None,
        description="Additional details about the change event that can be updated",
    )

    @computed_field
    @property
    def type(self) -> Literal["change_event"]:
        """Return the type of this object."""
        return "change_event"


class ChangeEventQuery(BaseModel):
    """Query parameters for listing change events."""

    model_config = ConfigDict(extra="forbid")

    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="The number of results per page",
    )
    offset: int | None = Field(
        ge=0,
        default=None,
        description="The offset of the first record returned",
    )
    total: bool | None = Field(
        default=None,
        description="By default the total field is not included. Set to true to include it",
    )
    team_ids: list[str] | None = Field(
        default=None,
        description="An array of team IDs. Only results related to these teams will be returned",
    )
    integration_ids: list[str] | None = Field(
        default=None,
        description="An array of integration IDs. Only results related to these integrations will be returned",
    )
    since: datetime | None = Field(
        default=None,
        description="The start of the date range over which you want to search",
    )
    until: datetime | None = Field(
        default=None,
        description="The end of the date range over which you want to search",
    )

    def to_params(self) -> dict[str, Any]:
        """Convert query model to API request parameters.

        Returns:
            Dictionary of query parameters formatted for the PagerDuty API
        """
        params = {}
        if self.limit:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.total is not None:
            params["total"] = self.total
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.integration_ids:
            params["integration_ids[]"] = self.integration_ids
        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        return params
