"""Tests for webhooks-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)

_SAMPLE_SUBSCRIPTION = {
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

_SAMPLE_SUBSCRIPTION_WITH_SECRET = {
    **_SAMPLE_SUBSCRIPTION,
    "id": "WH456",
    "delivery_method": {
        **_SAMPLE_SUBSCRIPTION["delivery_method"],
        "secret": "s3cr3t_signing_key",
    },
}

_SAMPLE_SERVICE_SUBSCRIPTION = {
    "id": "WH789",
    "type": "webhook_subscription",
    "active": True,
    "description": "Service webhook",
    "delivery_method": {
        "id": "DM456",
        "type": "http_delivery_method",
        "url": "https://example.com/service-hook",
    },
    "events": ["incident.triggered", "incident.resolved"],
    "filter": {"type": "service_reference", "id": "SVC123"},
}

_SAMPLE_EXTENSION_SCHEMA = {
    "id": "PJFWPEP",
    "type": "extension_schema",
    "summary": "Generic Webhook",
    "label": "Generic Webhook",
    "key": "generic_webhook",
    "description": "Send events to a generic webhook endpoint",
    "guide_url": "https://developer.pagerduty.com/docs/webhooks",
}


class WebhooksCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for webhooks-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_webhook_subscriptions",
                parameters=lambda params: True,
                response={
                    "response": [_SAMPLE_SUBSCRIPTION, _SAMPLE_SERVICE_SUBSCRIPTION]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_webhook_subscription",
                parameters=lambda params: params.get("subscription_id") == "WH123",
                response=_SAMPLE_SUBSCRIPTION,
            ),
            MockMCPToolInvocationResponse(
                tool_name="create_webhook_subscription",
                parameters=lambda params: True,
                response=_SAMPLE_SUBSCRIPTION_WITH_SECRET,
            ),
            MockMCPToolInvocationResponse(
                tool_name="update_webhook_subscription",
                parameters=lambda params: True,
                response={**_SAMPLE_SUBSCRIPTION, "active": False},
            ),
            MockMCPToolInvocationResponse(
                tool_name="delete_webhook_subscription",
                parameters=lambda params: True,
                response=None,
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_extension_schemas",
                parameters=lambda params: True,
                response={"response": [_SAMPLE_EXTENSION_SCHEMA]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_extension_schema",
                parameters=lambda params: params.get("schema_id") == "PJFWPEP",
                response=_SAMPLE_EXTENSION_SCHEMA,
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


WEBHOOK_COMPETENCY_TESTS = [
    # list_webhook_subscriptions
    WebhooksCompetencyTest(
        query="Show me all webhook subscriptions",
        expected_tool_calls=[
            MockToolCall(name="list_webhook_subscriptions", parameters={})
        ],
        description="Basic webhook subscriptions listing",
    ),
    WebhooksCompetencyTest(
        query="List webhook subscriptions scoped to services",
        expected_tool_calls=[
            MockToolCall(
                name="list_webhook_subscriptions",
                parameters={"filter_type": "service_reference"},
            )
        ],
        description="List webhook subscriptions filtered by service scope",
    ),
    WebhooksCompetencyTest(
        query="Show me the first 5 account-level webhook subscriptions",
        expected_tool_calls=[
            MockToolCall(
                name="list_webhook_subscriptions",
                parameters={"filter_type": "account_reference", "limit": 5},
            )
        ],
        description="List webhook subscriptions with filter_type and limit",
    ),
    # get_webhook_subscription
    WebhooksCompetencyTest(
        query="Get details for webhook subscription WH123",
        expected_tool_calls=[
            MockToolCall(
                name="get_webhook_subscription",
                parameters={"subscription_id": "WH123"},
            )
        ],
        description="Get a specific webhook subscription by ID",
    ),
    # create_webhook_subscription — account-wide
    WebhooksCompetencyTest(
        query=(
            "Create a webhook subscription that sends incident.triggered and incident.resolved "
            "events to https://example.com/hook for the whole account"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_webhook_subscription",
                parameters={
                    "webhook_data": {
                        "delivery_method": {
                            "type": "http_delivery_method",
                            "url": "https://example.com/hook",
                        },
                        "events": ["incident.triggered", "incident.resolved"],
                        "filter": {"type": "account_reference"},
                    }
                },
            )
        ],
        description="Create account-scoped webhook subscription",
    ),
    # create_webhook_subscription — service-scoped
    WebhooksCompetencyTest(
        query=(
            "Create a webhook subscription for service SVC123 that delivers "
            "incident.triggered events to https://example.com/service-hook"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="create_webhook_subscription",
                parameters={
                    "webhook_data": {
                        "delivery_method": {
                            "type": "http_delivery_method",
                            "url": "https://example.com/service-hook",
                        },
                        "events": ["incident.triggered"],
                        "filter": {"type": "service_reference", "id": "SVC123"},
                    }
                },
            )
        ],
        description="Create service-scoped webhook subscription",
    ),
    # update_webhook_subscription — disable
    WebhooksCompetencyTest(
        query="Disable webhook subscription WH123",
        expected_tool_calls=[
            MockToolCall(
                name="update_webhook_subscription",
                parameters={
                    "subscription_id": "WH123",
                    "webhook_data": {"active": False},
                },
            )
        ],
        description="Disable a webhook subscription",
    ),
    # update_webhook_subscription — change events
    # The model fetches the current subscription first to see the existing event list,
    # then issues the update with the merged set.
    WebhooksCompetencyTest(
        query=(
            "Update webhook subscription WH123 to also receive incident.acknowledged events"
        ),
        expected_tool_calls=[
            MockToolCall(
                name="get_webhook_subscription",
                parameters={"subscription_id": "WH123"},
            ),
            MockToolCall(
                name="update_webhook_subscription",
                parameters={
                    "subscription_id": "WH123",
                    "webhook_data": {
                        "events": [
                            "incident.triggered",
                            "incident.acknowledged",
                            "incident.resolved",
                        ]
                    },
                },
            ),
        ],
        description="Update webhook subscription event types",
    ),
    # delete_webhook_subscription
    WebhooksCompetencyTest(
        query="Delete webhook subscription WH123",
        expected_tool_calls=[
            MockToolCall(
                name="delete_webhook_subscription",
                parameters={"subscription_id": "WH123"},
            )
        ],
        description="Delete a webhook subscription",
    ),
    # list_extension_schemas
    WebhooksCompetencyTest(
        query="What extension schemas are available in PagerDuty?",
        expected_tool_calls=[
            MockToolCall(name="list_extension_schemas", parameters={})
        ],
        description="List all available extension schemas",
    ),
    # get_extension_schema
    WebhooksCompetencyTest(
        query="Get details for extension schema PJFWPEP",
        expected_tool_calls=[
            MockToolCall(
                name="get_extension_schema",
                parameters={"schema_id": "PJFWPEP"},
            )
        ],
        description="Get a specific extension schema by ID",
    ),
]
