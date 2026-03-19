---
sidebar_position: 7
---

# Services

Services represent components of your infrastructure or application. Each service has an escalation policy and alert grouping settings that determine how incidents are created and routed.

## Tools

### `list_services`

List all services with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `ServiceQuery` | No | Optional filtering parameters (name, team, etc.) |

**Example prompt:**

> "List all services owned by the platform team"

---

### `get_service`

Get details for a specific service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_id` | `string` | Yes | The ID of the service to retrieve |

**Example prompt:**

> "Get details for the payment-gateway service"

---

### `create_service` *(write)*

Create a new service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_data` | `ServiceCreate` | Yes | The data for the new service. Do not include `id` — it is auto-generated. The `escalation_policy` reference requires only the `id` field, e.g. `{"id": "PXXXXXX"}` |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create a new service called 'checkout-api' with escalation policy PXXXXXX"

---

### `update_service` *(write)*

Update an existing service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_id` | `string` | Yes | The ID of the service to update |
| `service_data` | `ServiceCreate` | Yes | The updated service data |

:::note
Requires `--enable-write-tools` flag.
:::
