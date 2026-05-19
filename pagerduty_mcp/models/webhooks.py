from typing import Any, Literal

from pydantic import BaseModel, Field


class WebhookCustomHeader(BaseModel):
    name: str = Field(description="The header name")
    value: str = Field(description="The header value")


class WebhookDeliveryMethod(BaseModel):
    """HTTP delivery method for a webhook subscription."""

    type: str = Field(default="http_delivery_method", description="The delivery method type")
    url: str = Field(description="The destination URL for webhook delivery")
    custom_headers: list[WebhookCustomHeader] | None = Field(
        default=None, description="Optional custom headers to include with each webhook delivery"
    )
    # Read-only fields (populated in responses)
    id: str | None = Field(default=None, description="The delivery method ID (read-only)")
    secret: str | None = Field(
        default=None,
        description=(
            "The signing secret for this webhook. "
            "Only returned on the initial create response — store it securely."
        ),
    )
    temporarily_disabled: bool | None = Field(
        default=None,
        description="True if the webhook is temporarily disabled due to repeated delivery failures",
    )


class WebhookFilter(BaseModel):
    """Scope filter for a webhook subscription."""

    type: Literal["account_reference", "service_reference", "team_reference"] = Field(
        description="The scope of events to receive: account-wide, a specific service, or a specific team"
    )
    id: str | None = Field(
        default=None,
        description="The ID of the service or team to filter on (required for service/team scope)",
    )


class WebhookSubscription(BaseModel):
    """A PagerDuty webhook subscription."""

    id: str | None = Field(default=None, description="The webhook subscription ID (read-only)")
    type: str | None = Field(default=None, description="The object type (always webhook_subscription)")
    active: bool | None = Field(
        default=None, description="Whether the subscription will produce webhook events"
    )
    description: str | None = Field(default=None, description="A short description of the webhook subscription")
    delivery_method: WebhookDeliveryMethod | None = Field(
        default=None, description="The delivery method configuration"
    )
    events: list[str] | None = Field(
        default=None, description="The outbound event types this webhook will receive"
    )
    filter: WebhookFilter | None = Field(
        default=None, description="The scope filter for this webhook subscription"
    )


class WebhookCreate(BaseModel):
    """Request body for creating a webhook subscription."""

    type: str = Field(default="webhook_subscription", description="Must be webhook_subscription")
    delivery_method: WebhookDeliveryMethod = Field(
        description="The delivery configuration — must include type and url"
    )
    events: list[str] = Field(
        description=(
            "The event types to subscribe to (e.g. incident.triggered, incident.resolved, "
            "incident.acknowledged, service.updated). At least one event is required."
        )
    )
    filter: WebhookFilter = Field(
        description=(
            "The scope filter — account_reference for all events, "
            "or service_reference/team_reference for specific resources"
        )
    )
    active: bool | None = Field(default=None, description="Whether the subscription should be active on creation")
    description: str | None = Field(default=None, description="A short description of this webhook subscription")


class WebhookUpdate(BaseModel):
    """Request body for updating a webhook subscription. All fields are optional."""

    active: bool | None = Field(default=None, description="Enable or disable the webhook subscription")
    description: str | None = Field(default=None, description="Updated description")
    delivery_method: dict[str, Any] | None = Field(
        default=None, description="Updated delivery method (provide only fields to change)"
    )
    events: list[str] | None = Field(default=None, description="Updated list of event types to subscribe to")
    filter: WebhookFilter | None = Field(default=None, description="Updated scope filter")


class ExtensionSchema(BaseModel):
    """A PagerDuty extension schema (extension vendor definition)."""

    id: str | None = Field(default=None, description="The extension schema ID")
    type: str | None = Field(default=None, description="The object type (always extension_schema)")
    summary: str | None = Field(default=None, description="A short-form summary of the extension schema")
    label: str | None = Field(default=None, description="Human-friendly display label")
    key: str | None = Field(default=None, description="Machine-friendly display label")
    description: str | None = Field(default=None, description="A long description of the extension")
    icon_url: str | None = Field(default=None, description="URL for the small (18x18) logo")
    logo_url: str | None = Field(default=None, description="URL for the large logo (75px high, max 300px wide)")
    guide_url: str | None = Field(default=None, description="Link to the extension's support guide")
    url: str | None = Field(default=None, description="The webhook payload destination URL for this extension")
    send_types: list[str] | None = Field(
        default=None,
        description="The PagerDuty incident event types that activate this extension",
    )
