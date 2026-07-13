import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.webhooks import (
    ExtensionSchema,
    WebhookCreate,
    WebhookDeliveryMethod,
    WebhookFilter,
    WebhookSubscription,
    WebhookUpdate,
)
from pagerduty_mcp.tools.webhooks import (
    create_webhook_subscription,
    delete_webhook_subscription,
    get_extension_schema,
    get_webhook_subscription,
    list_extension_schemas,
    list_webhook_subscriptions,
    update_webhook_subscription,
)


class TestWebhookModels(unittest.TestCase):
    """Test webhook model validation."""

    def test_webhook_subscription_model(self):
        """Test WebhookSubscription can be constructed from API response."""
        data = {
            "id": "WH123",
            "type": "webhook_subscription",
            "active": True,
            "description": "Test webhook",
            "delivery_method": {"type": "http_delivery_method", "url": "https://example.com/hook"},
            "events": ["incident.triggered", "incident.resolved"],
            "filter": {"type": "account_reference"},
        }
        sub = WebhookSubscription(**data)
        self.assertEqual(sub.id, "WH123")
        self.assertEqual(sub.active, True)
        self.assertIsInstance(sub.delivery_method, WebhookDeliveryMethod)
        self.assertIsInstance(sub.filter, WebhookFilter)

    def test_webhook_create_serialization(self):
        """Test WebhookCreate serializes correctly for API call."""
        create = WebhookCreate(
            delivery_method=WebhookDeliveryMethod(
                type="http_delivery_method",
                url="https://example.com/hook",
            ),
            events=["incident.triggered"],
            filter=WebhookFilter(type="account_reference"),
            description="My webhook",
        )
        dumped = create.model_dump(exclude_none=True)
        self.assertEqual(dumped["delivery_method"]["url"], "https://example.com/hook")
        self.assertEqual(dumped["events"], ["incident.triggered"])
        self.assertEqual(dumped["filter"]["type"], "account_reference")

    def test_webhook_filter_types(self):
        """Test all three WebhookFilter type values are accepted."""
        for ftype in ("account_reference", "service_reference", "team_reference"):
            f = WebhookFilter(type=ftype)
            self.assertEqual(f.type, ftype)

    def test_webhook_update_partial(self):
        """Test WebhookUpdate with only some fields set."""
        update = WebhookUpdate(active=False)
        dumped = update.model_dump(exclude_none=True)
        self.assertEqual(dumped["active"], False)
        self.assertNotIn("events", dumped)

    def test_extension_schema_model(self):
        """Test ExtensionSchema construction."""
        schema = ExtensionSchema(
            id="PJFWPEP",
            type="extension_schema",
            label="Generic Webhook",
            key="generic_webhook",
            description="Send events to a generic webhook endpoint",
        )
        self.assertEqual(schema.id, "PJFWPEP")
        self.assertEqual(schema.label, "Generic Webhook")


class TestWebhookSubscriptionTools(unittest.TestCase):
    """Test webhook subscription tool functions."""

    @classmethod
    def setUpClass(cls):
        cls.sample_subscription = {
            "id": "WH123",
            "type": "webhook_subscription",
            "active": True,
            "description": "Incident alerts",
            "delivery_method": {
                "id": "DM123",
                "type": "http_delivery_method",
                "url": "https://example.com/hook",
            },
            "events": ["incident.triggered", "incident.resolved"],
            "filter": {"type": "account_reference"},
        }
        cls.mock_client = MagicMock()

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None
        self.mock_client.rput.side_effect = None
        self.mock_client.rdelete.side_effect = None

    @patch("pagerduty_mcp.tools.webhooks.paginate")
    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_list_webhook_subscriptions_no_filters(self, mock_get_client, mock_paginate):
        """Test listing webhook subscriptions without filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_subscription]

        result = list_webhook_subscriptions()

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="webhook_subscriptions", params={}, maximum_records=1000
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], WebhookSubscription)
        self.assertEqual(result.response[0].id, "WH123")

    @patch("pagerduty_mcp.tools.webhooks.paginate")
    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_list_webhook_subscriptions_with_filter_type(self, mock_get_client, mock_paginate):
        """Test listing webhook subscriptions filtered by type."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_subscription]

        list_webhook_subscriptions(filter_type="account_reference", limit=25)

        mock_paginate.assert_called_once_with(
            client=self.mock_client,
            entity="webhook_subscriptions",
            params={"filter_type": "account_reference", "limit": 25},
            maximum_records=25,
        )

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_get_webhook_subscription_wrapped(self, mock_get_client):
        """Test get_webhook_subscription with wrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = {"webhook_subscription": self.sample_subscription}

        result = get_webhook_subscription("WH123")

        self.mock_client.rget.assert_called_once_with("/webhook_subscriptions/WH123")
        self.assertIsInstance(result, WebhookSubscription)
        self.assertEqual(result.id, "WH123")

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_get_webhook_subscription_unwrapped(self, mock_get_client):
        """Test get_webhook_subscription with SDK-unwrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_subscription

        result = get_webhook_subscription("WH123")

        self.assertIsInstance(result, WebhookSubscription)
        self.assertEqual(result.id, "WH123")

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_create_webhook_subscription(self, mock_get_client):
        """Test create_webhook_subscription posts correct payload."""
        mock_get_client.return_value = self.mock_client
        # Simulate response with signing secret (only on create)
        response_with_secret = dict(self.sample_subscription)
        response_with_secret["delivery_method"] = dict(self.sample_subscription["delivery_method"])
        response_with_secret["delivery_method"]["secret"] = "s3cr3t_signing_key"
        self.mock_client.rpost.return_value = {"webhook_subscription": response_with_secret}

        webhook_data = WebhookCreate(
            delivery_method=WebhookDeliveryMethod(
                type="http_delivery_method",
                url="https://example.com/hook",
            ),
            events=["incident.triggered", "incident.resolved"],
            filter=WebhookFilter(type="account_reference"),
            description="Incident alerts",
        )

        result = create_webhook_subscription(webhook_data)

        self.mock_client.rpost.assert_called_once_with(
            "/webhook_subscriptions",
            json={"webhook_subscription": webhook_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, WebhookSubscription)
        self.assertEqual(result.id, "WH123")
        # Verify the signing secret is surfaced in the response
        self.assertEqual(result.delivery_method.secret, "s3cr3t_signing_key")

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_create_webhook_subscription_unwrapped(self, mock_get_client):
        """Test create_webhook_subscription handles SDK-unwrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = self.sample_subscription

        webhook_data = WebhookCreate(
            delivery_method=WebhookDeliveryMethod(
                type="http_delivery_method",
                url="https://example.com/hook",
            ),
            events=["incident.triggered"],
            filter=WebhookFilter(type="account_reference"),
        )

        result = create_webhook_subscription(webhook_data)

        self.assertIsInstance(result, WebhookSubscription)
        self.assertEqual(result.id, "WH123")

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_update_webhook_subscription(self, mock_get_client):
        """Test update_webhook_subscription puts correct payload."""
        mock_get_client.return_value = self.mock_client
        updated = dict(self.sample_subscription)
        updated["active"] = False
        self.mock_client.rput.return_value = {"webhook_subscription": updated}

        update_data = WebhookUpdate(active=False)

        result = update_webhook_subscription("WH123", update_data)

        self.mock_client.rput.assert_called_once_with(
            "/webhook_subscriptions/WH123",
            json={"webhook_subscription": update_data.model_dump(exclude_none=True)},
        )
        self.assertIsInstance(result, WebhookSubscription)

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_update_webhook_subscription_unwrapped(self, mock_get_client):
        """Test update_webhook_subscription handles SDK-unwrapped response."""
        mock_get_client.return_value = self.mock_client
        updated = dict(self.sample_subscription)
        updated["active"] = False
        self.mock_client.rput.return_value = updated

        update_data = WebhookUpdate(active=False)

        result = update_webhook_subscription("WH123", update_data)

        self.assertIsInstance(result, WebhookSubscription)
        self.assertEqual(result.active, False)

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_delete_webhook_subscription(self, mock_get_client):
        """Test delete_webhook_subscription calls rdelete with correct path."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.return_value = None

        delete_webhook_subscription("WH123")

        self.mock_client.rdelete.assert_called_once_with("/webhook_subscriptions/WH123")


class TestExtensionSchemaTools(unittest.TestCase):
    """Test extension schema tool functions."""

    @classmethod
    def setUpClass(cls):
        cls.sample_schema = {
            "id": "PJFWPEP",
            "type": "extension_schema",
            "summary": "Generic Webhook",
            "label": "Generic Webhook",
            "key": "generic_webhook",
            "description": "Send events to a webhook endpoint",
            "guide_url": "https://developer.pagerduty.com",
        }
        cls.mock_client = MagicMock()

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.rget.side_effect = None

    @patch("pagerduty_mcp.tools.webhooks.paginate")
    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_list_extension_schemas(self, mock_get_client, mock_paginate):
        """Test listing extension schemas."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_schema]

        result = list_extension_schemas()

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="extension_schemas", params={}, maximum_records=1000
        )
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], ExtensionSchema)
        self.assertEqual(result.response[0].id, "PJFWPEP")
        self.assertEqual(result.response[0].label, "Generic Webhook")

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_get_extension_schema_wrapped(self, mock_get_client):
        """Test get_extension_schema with wrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = {"extension_schema": self.sample_schema}

        result = get_extension_schema("PJFWPEP")

        self.mock_client.rget.assert_called_once_with("/extension_schemas/PJFWPEP")
        self.assertIsInstance(result, ExtensionSchema)
        self.assertEqual(result.id, "PJFWPEP")

    @patch("pagerduty_mcp.tools.webhooks.get_client")
    def test_get_extension_schema_unwrapped(self, mock_get_client):
        """Test get_extension_schema with SDK-unwrapped response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_schema

        result = get_extension_schema("PJFWPEP")

        self.assertIsInstance(result, ExtensionSchema)
        self.assertEqual(result.key, "generic_webhook")


if __name__ == "__main__":
    unittest.main()
