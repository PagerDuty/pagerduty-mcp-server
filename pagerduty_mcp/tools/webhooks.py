from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.webhooks import (
    ExtensionSchema,
    WebhookCreate,
    WebhookSubscription,
    WebhookUpdate,
)
from pagerduty_mcp.utils import paginate


def list_webhook_subscriptions(
    filter_type: str | None = None,
    limit: int | None = None,
) -> ListResponseModel[WebhookSubscription]:
    """List webhook subscriptions.

    Args:
        filter_type: Filter by scope type: 'account_reference', 'service_reference', or 'team_reference'
        limit: Max results to return

    Returns:
        List of webhook subscriptions
    """
    params: dict[str, Any] = {}
    if filter_type:
        params["filter_type"] = filter_type
    if limit:
        params["limit"] = limit
    response = paginate(client=get_client(), entity="webhook_subscriptions", params=params)
    subscriptions = [WebhookSubscription(**sub) for sub in response]
    return ListResponseModel[WebhookSubscription](response=subscriptions)


def get_webhook_subscription(subscription_id: str) -> WebhookSubscription:
    """Get a specific webhook subscription by ID.

    Args:
        subscription_id: The ID of the webhook subscription to retrieve

    Returns:
        Webhook subscription details
    """
    response = get_client().rget(f"/webhook_subscriptions/{subscription_id}")
    if isinstance(response, dict) and "webhook_subscription" in response:
        return WebhookSubscription.model_validate(response["webhook_subscription"])
    return WebhookSubscription.model_validate(response)


def create_webhook_subscription(webhook_data: WebhookCreate) -> WebhookSubscription:
    """Create a new webhook subscription.

    The signing secret is included in the delivery_method of the returned subscription.
    It is only returned on this initial create response — store it securely.

    Args:
        webhook_data: Configuration for the new webhook subscription, including
            delivery URL, event types, and scope filter

    Returns:
        The created webhook subscription (includes the one-time signing secret in delivery_method.secret)
    """
    payload = {"webhook_subscription": webhook_data.model_dump(exclude_none=True)}
    response = get_client().rpost("/webhook_subscriptions", json=payload)
    if isinstance(response, dict) and "webhook_subscription" in response:
        return WebhookSubscription.model_validate(response["webhook_subscription"])
    return WebhookSubscription.model_validate(response)


def update_webhook_subscription(subscription_id: str, webhook_data: WebhookUpdate) -> WebhookSubscription:
    """Update an existing webhook subscription.

    Args:
        subscription_id: The ID of the webhook subscription to update
        webhook_data: Fields to update (only provided fields are changed)

    Returns:
        The updated webhook subscription
    """
    payload = {"webhook_subscription": webhook_data.model_dump(exclude_none=True)}
    response = get_client().rput(f"/webhook_subscriptions/{subscription_id}", json=payload)
    if isinstance(response, dict) and "webhook_subscription" in response:
        return WebhookSubscription.model_validate(response["webhook_subscription"])
    return WebhookSubscription.model_validate(response)


def delete_webhook_subscription(subscription_id: str) -> None:
    """Delete a webhook subscription.

    Args:
        subscription_id: The ID of the webhook subscription to delete
    """
    get_client().rdelete(f"/webhook_subscriptions/{subscription_id}")


def list_extension_schemas(
    limit: int | None = None,
) -> ListResponseModel[ExtensionSchema]:
    """List available extension schemas (extension vendors).

    Extension schemas describe the available extension integrations that can be
    attached to PagerDuty services.

    Args:
        limit: Max results to return

    Returns:
        List of extension schemas
    """
    params: dict[str, Any] = {}
    if limit:
        params["limit"] = limit
    response = paginate(client=get_client(), entity="extension_schemas", params=params)
    schemas = [ExtensionSchema(**schema) for schema in response]
    return ListResponseModel[ExtensionSchema](response=schemas)


def get_extension_schema(schema_id: str) -> ExtensionSchema:
    """Get a specific extension schema by ID.

    Args:
        schema_id: The ID of the extension schema to retrieve

    Returns:
        Extension schema details
    """
    response = get_client().rget(f"/extension_schemas/{schema_id}")
    if isinstance(response, dict) and "extension_schema" in response:
        return ExtensionSchema.model_validate(response["extension_schema"])
    return ExtensionSchema.model_validate(response)
