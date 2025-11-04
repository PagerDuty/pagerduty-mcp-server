"""Models for PagerDuty AIOps MCP Server.

This module consolidates models from:
- Alert Grouping Settings
- Event Orchestrations
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.references import ServiceReference, TeamReference, UserReference


# =============================================================================
# COMMON MODELS
# =============================================================================


class ListResponseModel[T](BaseModel):
    """Generic list response model."""

    response: list[T] = Field(description="The list of resources returned")


# =============================================================================
# ALERT GROUPING SETTINGS MODELS
# =============================================================================


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


class CreateAlertGroupingSettingRequest(BaseModel):
    """Request wrapper for creating an alert grouping setting."""

    alert_grouping_setting: AlertGroupingSettingCreate = Field(description="The alert grouping setting to create")


class UpdateAlertGroupingSettingRequest(BaseModel):
    """Request wrapper for updating an alert grouping setting."""

    alert_grouping_setting: AlertGroupingSettingCreate = Field(
        description="The alert grouping setting updates to apply"
    )


# =============================================================================
# EVENT ORCHESTRATION MODELS
# =============================================================================


class EventOrchestrationIntegration(BaseModel):
    id: str = Field(description="ID of the Integration.", json_schema_extra={"readOnly": True})
    label: str = Field(description="Name of the Integration.")
    parameters: dict[str, Any] = Field(description="Integration parameters", json_schema_extra={"readOnly": True})


class EventOrchestration(BaseModel):
    id: str = Field(description="ID of the Orchestration.", json_schema_extra={"readOnly": True})
    self: str = Field(
        description="The API show URL at which the object is accessible", json_schema_extra={"readOnly": True}
    )
    name: str = Field(description="Name of the Orchestration.")
    description: str | None = Field(description="A description of this Orchestration's purpose.", default=None)
    team: TeamReference | None = Field(
        description="Reference to the team that owns the Orchestration. If none is specified, only admins have access.",
        default=None,
    )
    integrations: list[EventOrchestrationIntegration] | None = Field(
        description="List of integrations for the orchestration", default=None, json_schema_extra={"readOnly": True}
    )
    routes: int = Field(
        description="Number of different Service Orchestration being routed to", json_schema_extra={"readOnly": True}
    )
    created_at: datetime = Field(
        description="The date the Orchestration was created at.", json_schema_extra={"readOnly": True}
    )
    created_by: UserReference | None = Field(
        description="Reference to the user that has created the Orchestration.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    updated_at: datetime = Field(
        description="The date the Orchestration was last updated.", json_schema_extra={"readOnly": True}
    )
    updated_by: UserReference | None = Field(
        description="Reference to the user that has updated the Orchestration last.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    version: str | None = Field(
        description="Version of the Orchestration.", json_schema_extra={"readOnly": True}, default=None
    )

    @computed_field
    @property
    def type(self) -> Literal["event_orchestration"]:
        return "event_orchestration"


class EventOrchestrationQuery(BaseModel):
    limit: int | None = Field(
        ge=1,
        le=MAXIMUM_PAGINATION_LIMIT,
        default=DEFAULT_PAGINATION_LIMIT,
        description="The number of results per page.",
    )
    offset: int | None = Field(ge=0, default=None, description="Offset to start pagination search results.")
    sort_by: (
        Literal["name:asc", "name:desc", "routes:asc", "routes:desc", "created_at:asc", "created_at:desc"] | None
    ) = Field(default="name:asc", description="Used to specify the field you wish to sort the results on.")

    def to_params(self) -> dict[str, Any]:
        params = {}
        if self.limit:
            params["limit"] = self.limit
        if self.offset:
            params["offset"] = self.offset
        if self.sort_by:
            params["sort_by"] = self.sort_by
        return params


# Router-specific models
class EventOrchestrationRuleCondition(BaseModel):
    expression: str = Field(
        description="A PCL condition string",
        json_schema_extra={"example": "event.summary matches part 'my service error'"},
    )


class EventOrchestrationRuleActions(BaseModel):
    route_to: str | None = Field(
        description=(
            "The ID of the target Service for the resulting alert. "
            "You can find the service you want to route to by calling the services endpoint."
        ),
        default=None,
        json_schema_extra={"example": "PSI2I2O"},
    )
    dynamic_route_to: dict[str, Any] | None = Field(
        description=(
            "Use the contents of an event payload to dynamically route an event to the target service. "
            "Available to AIOps customers."
        ),
        default=None,
    )


class EventOrchestrationRule(BaseModel):
    id: str = Field(description="ID of the rule", json_schema_extra={"readOnly": True})
    label: str | None = Field(description="A description of this rule's purpose.", default=None)
    conditions: list[EventOrchestrationRuleCondition] = Field(
        description=(
            "Each of these conditions is evaluated to check if an event matches this rule. "
            "The rule is considered a match if **any** of these conditions match."
        )
    )
    actions: EventOrchestrationRuleActions = Field(
        description=(
            "When an event matches this rule, these are the actions that will be taken "
            "to change the resulting alert and incident."
        )
    )
    disabled: bool | None = Field(
        description="Indicates whether the rule is disabled and would therefore not be evaluated.", default=False
    )


class EventOrchestrationRuleSet(BaseModel):
    id: str = Field(
        description=(
            "The ID of this set of rules. Rules in other sets can route events into this set "
            "using the 'route_to' properties."
        ),
        default="start",
    )
    rules: list[EventOrchestrationRule] = Field(description="List of rules in this set")


class EventOrchestrationCatchAll(BaseModel):
    actions: EventOrchestrationRuleActions = Field(
        description="These are the actions that will be taken to change the resulting alert and incident."
    )


class EventOrchestrationParent(BaseModel):
    id: str = Field(description="ID of the Global Event Orchestration this Router belongs to.")
    type: Literal["event_orchestration_reference"] = Field(
        description="A string that determines the schema of the parent object", json_schema_extra={"readOnly": True}
    )
    self: str = Field(
        description="The API show URL at which the parent object is accessible", json_schema_extra={"readOnly": True}
    )


class EventOrchestrationPath(BaseModel):
    type: Literal["router"] = Field(
        description="Indicates that these are a 'router' type set of rules.", default="router"
    )
    parent: EventOrchestrationParent = Field(json_schema_extra={"readOnly": True})
    self: str | None = Field(
        description="The API show URL at which the object is accessible",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    sets: list[EventOrchestrationRuleSet] = Field(
        description=(
            "The Router contains a single set of rules (the 'start' set). "
            "The Router evaluates Events against these Rules, one at a time, "
            "and routes each Event to a specific Service based on the first rule that matches."
        ),
        max_length=1,
    )
    catch_all: EventOrchestrationCatchAll = Field(
        description=(
            "When none of the rules match an event, the event will be routed according to the catch_all settings."
        )
    )
    created_at: datetime = Field(
        description="The date/time the object was created.", json_schema_extra={"readOnly": True}
    )
    created_by: UserReference | None = Field(
        description="Reference to the user that created the object.", json_schema_extra={"readOnly": True}, default=None
    )
    updated_at: datetime = Field(
        description="The date/time the object was last updated.", json_schema_extra={"readOnly": True}
    )
    updated_by: UserReference | None = Field(
        description="Reference to the user that last updated the object.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    version: str = Field(description="Version of these Orchestration Rules", json_schema_extra={"readOnly": True})


class EventOrchestrationRouter(BaseModel):
    orchestration_path: EventOrchestrationPath | None = Field(
        description="The orchestration router path configuration", default=None
    )

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "EventOrchestrationRouter":
        """Create EventOrchestrationRouter from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Wrapped: {"orchestration_path": {...}}
        - Direct: {...} (router data directly)
        """
        if "orchestration_path" in response_data:
            return cls.model_validate(response_data)

        return cls(orchestration_path=EventOrchestrationPath.model_validate(response_data))


class EventOrchestrationPathUpdateRequest(BaseModel):
    """Orchestration path model for update requests, excluding readonly fields."""

    type: Literal["router"] = Field(
        description="Indicates that these are a 'router' type set of rules.", default="router"
    )
    sets: list[EventOrchestrationRuleSet] = Field(
        description=(
            "The Router contains a single set of rules (the 'start' set). "
            "The Router evaluates Events against these Rules, one at a time, "
            "and routes each Event to a specific Service based on the first rule that matches."
        ),
        max_length=1,
    )
    catch_all: EventOrchestrationCatchAll = Field(
        description=(
            "When none of the rules match an event, the event will be routed according to the catch_all settings."
        )
    )


class EventOrchestrationRouterUpdateRequest(BaseModel):
    """Request model for updating an event orchestration router configuration."""

    orchestration_path: EventOrchestrationPathUpdateRequest = Field(
        description="The orchestration router path configuration to update"
    )

    @classmethod
    def from_path(cls, path: EventOrchestrationPath) -> "EventOrchestrationRouterUpdateRequest":
        """Create update request from an EventOrchestrationPath, excluding readonly fields."""
        update_path = EventOrchestrationPathUpdateRequest(type=path.type, sets=path.sets, catch_all=path.catch_all)
        return cls(orchestration_path=update_path)


class AppendRouterRuleRequest(BaseModel):
    """Request model for creating a new event orchestration rule."""

    label: str | None = Field(description="A description of this rule's purpose.", default=None)
    conditions: list[EventOrchestrationRuleCondition] = Field(
        description=(
            "Each of these conditions is evaluated to check if an event matches this rule. "
            "The rule is considered a match if **any** of these conditions match."
        )
    )
    actions: EventOrchestrationRuleActions = Field(
        description=(
            "When an event matches this rule, these are the actions that will be taken "
            "to change the resulting alert and incident."
        )
    )
    disabled: bool | None = Field(
        description="Indicates whether the rule is disabled and would therefore not be evaluated.", default=False
    )


class EventOrchestrationServiceParent(BaseModel):
    """Parent reference for a Service Orchestration."""

    id: str = Field(
        description="The ID of the Service this Orchestration belongs to.", json_schema_extra={"readOnly": True}
    )
    type: Literal["service_reference"] = Field(
        description="A string that determines the schema of the parent object", json_schema_extra={"readOnly": True}
    )
    self: str = Field(
        description="The API show URL at which the parent object is accessible", json_schema_extra={"readOnly": True}
    )


class EventOrchestrationGlobalParent(BaseModel):
    """Parent reference for a Global Orchestration."""

    id: str = Field(
        description="ID of the Global Event Orchestration these Global Rules belongs to.",
        json_schema_extra={"readOnly": True},
    )
    type: Literal["event_orchestration_reference"] = Field(
        description="A string that determines the schema of the parent object", json_schema_extra={"readOnly": True}
    )
    self: str = Field(
        description="The API show URL at which the parent object is accessible", json_schema_extra={"readOnly": True}
    )


class EventOrchestrationPathActionsBase(BaseModel):
    """Base actions for orchestration rules - common to both service and global."""

    route_to: str | None = Field(
        description=(
            "The ID of a Set from this Orchestration whose rules you also want to use "
            "with events that match this rule."
        ),
        default=None,
    )
    suppress: bool | None = Field(
        description="If true, the resulting alert is suppressed. Suppressed alerts will not trigger an incident.",
        default=None,
    )
    suspend: int | None = Field(
        description="The number of seconds to suspend the resulting alert before triggering.",
        default=None,
    )
    priority: str | None = Field(
        description="The ID of the priority you want to set on resulting incident.",
        default=None,
        json_schema_extra={"example": "P53ZZH5"},
    )
    escalation_policy: str | None = Field(
        description="The ID of the Escalation Policy you want to assign incidents to.",
        default=None,
        json_schema_extra={"example": "PQOMK4S"},
    )
    annotate: str | None = Field(
        description="Add this text as a note on the resulting incident.",
        default=None,
    )
    severity: Literal["info", "error", "warning", "critical"] | None = Field(
        description="Set the severity of the resulting alert.",
        default=None,
    )
    event_action: Literal["trigger", "resolve"] | None = Field(
        description="Set whether the resulting alert status is trigger or resolve.",
        default=None,
    )
    variables: list[dict[str, Any]] | None = Field(
        description="Populate variables from event payloads and use those variables in other event actions.",
        default=None,
    )
    extractions: list[dict[str, Any]] | None = Field(
        description="Dynamically extract values to set and modify new and existing PD-CEF fields.",
        default=None,
    )
    automation_actions: list[dict[str, Any]] | None = Field(
        description="Create a Webhook associated with the resulting incident.",
        default=None,
    )
    incident_custom_field_updates: list[dict[str, Any]] | None = Field(
        description="Configure custom field updates for the incident.",
        default=None,
    )


class EventOrchestrationServiceActions(EventOrchestrationPathActionsBase):
    """Actions for Service Orchestration rules."""

    pagerduty_automation_actions: list[dict[str, Any]] | None = Field(
        description="Configure an Automation Action to be run for certain alert states.",
        default=None,
    )


class EventOrchestrationGlobalActions(EventOrchestrationPathActionsBase):
    """Actions for Global Orchestration rules."""

    drop_event: bool | None = Field(
        description=(
            "If true, this event will be dropped. Dropped events will not trigger or resolve "
            "an alert or an incident."
        ),
        default=None,
    )


class EventOrchestrationPathRuleBase(BaseModel):
    """Base rule model for orchestration paths."""

    id: str = Field(description="ID of the rule", json_schema_extra={"readOnly": True})
    label: str | None = Field(description="A description of this rule's purpose.", default=None)
    conditions: list[EventOrchestrationRuleCondition] = Field(
        description="Each of these conditions is evaluated to check if an event matches this rule."
    )
    disabled: bool | None = Field(
        description="Indicates whether the rule is disabled and would therefore not be evaluated.", default=False
    )


class EventOrchestrationServiceRule(EventOrchestrationPathRuleBase):
    """Rule for Service Orchestration."""

    actions: EventOrchestrationServiceActions = Field(
        description="When an event matches this rule, these are the actions that will be taken."
    )


class EventOrchestrationGlobalRule(EventOrchestrationPathRuleBase):
    """Rule for Global Orchestration."""

    actions: EventOrchestrationGlobalActions = Field(
        description="When an event matches this rule, these are the actions that will be taken."
    )


class EventOrchestrationPathRuleSetBase(BaseModel):
    """Base rule set model."""

    id: str = Field(
        description=(
            "The ID of this set of rules. Rules in other sets can route events into this set "
            "using the 'route_to' properties."
        ),
        default="start",
    )


class EventOrchestrationServiceRuleSet(EventOrchestrationPathRuleSetBase):
    """Rule set for Service Orchestration."""

    rules: list[EventOrchestrationServiceRule] = Field(description="List of rules in this set")


class EventOrchestrationGlobalRuleSet(EventOrchestrationPathRuleSetBase):
    """Rule set for Global Orchestration."""

    rules: list[EventOrchestrationGlobalRule] = Field(description="List of rules in this set")


class EventOrchestrationServiceCatchAll(BaseModel):
    """Catch-all actions for Service Orchestration."""

    actions: EventOrchestrationServiceActions = Field(
        description="These are the actions that will be taken when no rules match."
    )


class EventOrchestrationGlobalCatchAll(BaseModel):
    """Catch-all actions for Global Orchestration."""

    actions: EventOrchestrationGlobalActions = Field(
        description="These are the actions that will be taken when no rules match."
    )


class EventOrchestrationServicePath(BaseModel):
    """Service Orchestration path configuration."""

    type: Literal["service"] = Field(
        description="Indicates that these are sets of rules belonging to a service.",
        json_schema_extra={"readOnly": True},
    )
    parent: EventOrchestrationServiceParent = Field(json_schema_extra={"readOnly": True})
    self: str | None = Field(
        description="The API show URL at which the object is accessible",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    sets: list[EventOrchestrationServiceRuleSet] = Field(
        description=(
            "A Service Orchestration must contain at least a 'start' set, but can contain "
            "any number of additional sets."
        )
    )
    catch_all: EventOrchestrationServiceCatchAll = Field(
        description="When none of the Rules in a set match an event, we apply the catch_all actions to the event."
    )
    created_at: datetime | None = Field(
        description="The date/time the object was created.", json_schema_extra={"readOnly": True}, default=None
    )
    created_by: UserReference | None = Field(
        description="Reference to the user that created the object.", json_schema_extra={"readOnly": True}, default=None
    )
    updated_at: datetime | None = Field(
        description="The date/time the object was last updated.", json_schema_extra={"readOnly": True}, default=None
    )
    updated_by: UserReference | None = Field(
        description="Reference to the user that last updated the object.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    version: str | None = Field(
        description="Version of these Orchestration Rules", json_schema_extra={"readOnly": True}, default=None
    )
    migrated_at: datetime | None = Field(
        description="The date/time the service's Event Rules were converted to this Service Orchestration.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    migrated_by: UserReference | None = Field(
        description="Reference to the user that converted the service's Event Rules to this Service Orchestration.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    migrated_from: dict[str, Any] | None = Field(
        description="Reference to the Service Event Rules that were converted to this Service Orchestration.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    migrated_status: Literal["completed"] | None = Field(
        description="The status indicating whether the service's Event Rules were successfully converted.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    migrated_via: Literal["API", "UI"] | None = Field(
        description="Indicates whether the conversion was performed via the PagerDuty API or PagerDuty website.",
        json_schema_extra={"readOnly": True},
        default=None,
    )


class EventOrchestrationGlobalPath(BaseModel):
    """Global Orchestration path configuration."""

    type: Literal["global"] = Field(
        description="Indicates that these are a set of 'global' rules.", json_schema_extra={"readOnly": True}
    )
    parent: EventOrchestrationGlobalParent = Field(json_schema_extra={"readOnly": True})
    self: str | None = Field(
        description="The API show URL at which the object is accessible",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    sets: list[EventOrchestrationGlobalRuleSet] = Field(
        description="You must define at least a 'start' set, but you can also define any number of additional sets."
    )
    catch_all: EventOrchestrationGlobalCatchAll = Field(
        description=(
            "When none of the rules match an event, the event will be routed according to "
            "the catch_all settings."
        )
    )
    created_at: datetime | None = Field(
        description="The date/time the object was created.", json_schema_extra={"readOnly": True}, default=None
    )
    created_by: UserReference | None = Field(
        description="Reference to the user that created the object.", json_schema_extra={"readOnly": True}, default=None
    )
    updated_at: datetime | None = Field(
        description="The date/time the object was last updated.", json_schema_extra={"readOnly": True}, default=None
    )
    updated_by: UserReference | None = Field(
        description="Reference to the user that last updated the object.",
        json_schema_extra={"readOnly": True},
        default=None,
    )
    version: str | None = Field(
        description="Version of these Orchestration Rules", json_schema_extra={"readOnly": True}, default=None
    )


class EventOrchestrationService(BaseModel):
    """Service Orchestration response model."""

    orchestration_path: EventOrchestrationServicePath | None = Field(
        description="The orchestration service path configuration", default=None
    )

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "EventOrchestrationService":
        """Create EventOrchestrationService from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Wrapped: {"orchestration_path": {...}}
        - Direct: {...} (service orchestration data directly)
        """
        if "orchestration_path" in response_data:
            return cls.model_validate(response_data)

        return cls(orchestration_path=EventOrchestrationServicePath.model_validate(response_data))


class EventOrchestrationGlobal(BaseModel):
    """Global Orchestration response model."""

    orchestration_path: EventOrchestrationGlobalPath | None = Field(
        description="The orchestration global path configuration", default=None
    )

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "EventOrchestrationGlobal":
        """Create EventOrchestrationGlobal from PagerDuty API response.

        Handles both wrapped and direct response formats:
        - Wrapped: {"orchestration_path": {...}}
        - Direct: {...} (global orchestration data directly)
        """
        if "orchestration_path" in response_data:
            return cls.model_validate(response_data)

        return cls(orchestration_path=EventOrchestrationGlobalPath.model_validate(response_data))
