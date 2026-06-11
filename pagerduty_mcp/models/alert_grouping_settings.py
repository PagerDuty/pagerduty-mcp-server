from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import ServiceReference


class AlertGroupingSettingType(BaseModel):
    """Enum for alert grouping setting types."""

    CONTENT_BASED: Literal["content_based"] = "content_based"
    CONTENT_BASED_INTELLIGENT: Literal["content_based_intelligent"] = "content_based_intelligent"
    INTELLIGENT: Literal["intelligent"] = "intelligent"
    TIME: Literal["time"] = "time"


class AggregateType(BaseModel):
    """Enum for aggregate field matching types."""

    ALL: Literal["all"] = "all"
    ANY: Literal["any"] = "any"


class ContentBasedConfig(BaseModel):
    """Configuration for Content Based Alert Grouping."""

    aggregate: Literal["all", "any"] = Field(
        description="Whether Alerts should be grouped if 'all' or 'any' specified fields match. "
        "If 'all' is selected, an exact match on every specified field name must occur for Alerts to be grouped. "
        "If 'any' is selected, Alerts will be grouped when there is an exact match on at least one of the "
        "specified fields."
    )
    fields: list[str] = Field(
        description="An array of strings which represent the fields with which to group against. "
        "Depending on the aggregate, Alerts will group if some or all the fields match."
    )
    time_window: int = Field(
        ge=300,
        le=86400,
        description="The maximum amount of time allowed between Alerts. Any Alerts arriving greater than "
        "`time_window` seconds apart will not be grouped together. This is a rolling time window up to 24 hours "
        "and is counted from the most recently grouped alert. To use the 'recommended_time_window,' set the "
        "value to 0, otherwise the value must be between 300 <= time_window <= 3600 or 86400 (i.e. 24 hours).",
    )
    recommended_time_window: int | None = Field(
        default=None,
        description="In order to ensure your Service has the optimal grouping window, we use data science to calculate "
        "your Service's average Alert inter-arrival time. We encourage customer's to use this value, please set "
        "`time_window` to 0 to use the `recommended_time_window`.",
    )


class ContentBasedIntelligentConfig(BaseModel):
    """Configuration for Content Based Intelligent Alert Grouping."""

    aggregate: Literal["all", "any"] = Field(
        description="Whether Alerts should be grouped if 'all' or 'any' specified fields match. "
        "If 'all' is selected, an exact match on every specified field name must occur for Alerts to be grouped. "
        "If 'any' is selected, Alerts will be grouped when there is an exact match on at least one of the "
        "specified fields."
    )
    fields: list[str] = Field(
        description="An array of strings which represent the fields with which to group against. "
        "Depending on the aggregate, Alerts will group if some or all the fields match."
    )
    time_window: int = Field(
        ge=300,
        le=3600,
        description="The maximum amount of time allowed between Alerts. Any Alerts arriving greater than "
        "`time_window` seconds apart will not be grouped together. This is a rolling time window up to 24 hours "
        "and is counted from the most recently grouped alert. To use the 'recommended_time_window,' set the "
        "value to 0, otherwise the value must be between 300 <= time_window <= 3600.",
    )
    recommended_time_window: int | None = Field(
        default=None,
        description="In order to ensure your Service has the optimal grouping window, we use data science to calculate "
        "your Service's average Alert inter-arrival time. We encourage customer's to use this value, please set "
        "`time_window` to 0 to use the `recommended_time_window`.",
    )


class TimeGroupingConfig(BaseModel):
    """Configuration for Time Based Alert Grouping."""

    timeout: int = Field(
        ge=60,
        le=86400,
        description="The duration in seconds within which to automatically group incoming Alerts. "
        "To continue grouping Alerts until the Incident is resolved, set this value to 0.",
    )


class IntelligentGroupingConfig(BaseModel):
    """Configuration for Intelligent Alert Grouping."""

    time_window: int = Field(
        ge=300,
        le=3600,
        description="The maximum amount of time allowed between Alerts. Any Alerts arriving greater than "
        "`time_window` seconds apart will not be grouped together. This is a rolling time window up to 24 hours "
        "and is counted from the most recently grouped alert. To use the 'recommended_time_window,' set the "
        "value to 0, otherwise the value must be between 300 <= time_window <= 3600.",
    )
    recommended_time_window: int | None = Field(
        default=None,
        description="In order to ensure your Service has the optimal grouping window, we use data science to calculate "
        "your Service's average Alert inter-arrival time. We encourage customer's to use this value, please set "
        "`time_window` to 0 to use the `recommended_time_window`.",
    )
    iag_fields: list[str] = Field(
        default=["summary"],
        description="An array of strings which represent the iag fields with which to intelligently group against.",
    )


class AlertGroupingSetting(BaseModel):
    """Defines how alerts will be automatically grouped into incidents based on the configurations defined.

    Note that the Alert Grouping Setting features are available only on certain plans.
    """

    id: str | None = Field(default=None, description="The ID of the alert grouping setting")
    name: str | None = Field(
        default=None,
        description="An optional short-form string that provides succinct information about an AlertGroupingSetting "
        "object suitable for primary labeling of the entity. It is not intended to be an identifier.",
    )
    description: str | None = Field(
        default=None,
        description="An optional description in string that provides more information about an "
        "AlertGroupingSetting object.",
    )
    type: Literal["content_based", "content_based_intelligent", "intelligent", "time"] = Field(
        description="The type of alert grouping configuration"
    )
    config: ContentBasedConfig | ContentBasedIntelligentConfig | TimeGroupingConfig | IntelligentGroupingConfig = Field(
        description="The configuration for the alert grouping setting based on the type"
    )
    services: list[ServiceReference] = Field(
        description="The array of one or many Services with just ServiceID/name that the AlertGroupingSetting "
        "applies to. Type of content_based_intelligent allows for only one service in the array."
    )
    created_at: datetime | None = Field(
        default=None, description="The ISO8601 date/time an AlertGroupingSetting got created at."
    )
    updated_at: datetime | None = Field(
        default=None, description="The ISO8601 date/time an AlertGroupingSetting last got updated at."
    )

    @computed_field
    @property
    def type_literal(self) -> Literal["alert_grouping_setting"]:
        return "alert_grouping_setting"


class AlertGroupingSettingQuery(BaseModel):
    """Query parameters for listing alert grouping settings."""

    service_ids: list[str] | None = Field(
        default=None, description="An array of service IDs. Only results related to these services will be returned."
    )
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="The number of results per page.",
    )
    after: str | None = Field(
        default=None, description="Cursor to retrieve next page; only present if next page exists."
    )
    before: str | None = Field(
        default=None, description="Cursor to retrieve previous page; only present if not on first page."
    )
    total: bool = Field(
        default=False,
        description="By default the `total` field in pagination responses is set to `null` to provide the "
        "fastest possible response times. Set `total` to `true` for this field to be populated.",
    )

    def to_params(self) -> dict[str, Any]:
        """Convert to API query parameters."""
        params = {}
        if self.service_ids:
            params["service_ids[]"] = self.service_ids
        if self.limit:
            params["limit"] = self.limit
        if self.after:
            params["after"] = self.after
        if self.before:
            params["before"] = self.before
        if self.total:
            params["total"] = self.total
        return params


class AlertGroupingSettingCreate(BaseModel):
    """Alert grouping setting data for creation requests."""

    name: str | None = Field(
        default=None,
        description="An optional short-form string that provides succinct information about an AlertGroupingSetting "
        "object suitable for primary labeling of the entity.",
    )
    description: str | None = Field(
        default=None,
        description="An optional description that provides more information about an AlertGroupingSetting object.",
    )
    type: Literal["content_based", "content_based_intelligent", "intelligent", "time"] = Field(
        description="The type of alert grouping configuration"
    )
    config: ContentBasedConfig | ContentBasedIntelligentConfig | TimeGroupingConfig | IntelligentGroupingConfig = Field(
        description="The configuration for the alert grouping setting based on the type"
    )
    services: list[ServiceReference] = Field(
        description="The array of one or many Services that the AlertGroupingSetting applies to. "
        "Type of content_based_intelligent allows for only one service in the array."
    )


class AlertGroupingSettingCreateRequest(BaseModel):
    """Request wrapper for creating an alert grouping setting."""

    alert_grouping_setting: AlertGroupingSettingCreate = Field(description="The alert grouping setting to create")


class AlertGroupingSettingUpdateRequest(BaseModel):
    """Request wrapper for updating an alert grouping setting."""

    alert_grouping_setting: AlertGroupingSettingCreate = Field(
        description="The alert grouping setting updates to apply"
    )
