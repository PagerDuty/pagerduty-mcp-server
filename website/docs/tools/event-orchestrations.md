---
sidebar_position: 14
---

# Event Orchestrations

Event Orchestrations allow you to define rules for routing and transforming events before they create or update incidents. They can be configured at the global level, per-service level, or as routers that direct events to specific services.

## Tools

### `list_event_orchestrations`

List event orchestrations with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `EventOrchestrationQuery` | No | Optional filtering parameters |

---

### `get_event_orchestration`

Get details for a specific event orchestration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orchestration_id` | `string` | Yes | The ID of the event orchestration to retrieve |

---

### `get_event_orchestration_router`

Get the router configuration for a specific event orchestration. The router determines which service receives events based on matching rules.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orchestration_id` | `string` | Yes | The ID of the event orchestration |

---

### `get_event_orchestration_service`

Get the Service Orchestration configuration for a specific service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_id` | `string` | Yes | The ID of the service to retrieve the orchestration configuration for |

---

### `get_event_orchestration_global`

Get the Global Orchestration configuration for a specific event orchestration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orchestration_id` | `string` | Yes | The ID of the event orchestration |

---

### `update_event_orchestration_router` *(write)*

Update the router configuration for a specific event orchestration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orchestration_id` | `string` | Yes | The ID of the event orchestration to update router for |
| `router_update` | `EventOrchestrationRouterUpdateRequest` | Yes | The updated router configuration |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `append_event_orchestration_router_rule` *(write)*

Append a new routing rule to the end of an event orchestration's router rules. This tool first retrieves the current router configuration, appends the new rule to the existing rules array, and then updates the router.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `orchestration_id` | `string` | Yes | The ID of the event orchestration to append the rule to |
| `new_rule` | `EventOrchestrationRuleCreateRequest` | Yes | The new rule configuration to append |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Add a routing rule to orchestration PXXXXXX that sends events with severity=critical to the payments service"
