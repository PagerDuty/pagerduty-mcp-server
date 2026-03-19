---
sidebar_position: 4
---

# Change Events

Change Events represent changes to systems, services, and applications that can be correlated with incidents to provide context for troubleshooting. They help teams understand what changed before an incident occurred.

## Tools

### `list_change_events`

List all change events with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `ChangeEventQuery` | No | Query parameters for filtering change events |

**Example prompt:**

> "List recent change events from the last 24 hours"

---

### `get_change_event`

Get details about a specific change event.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `change_event_id` | `string` | Yes | The ID of the change event to retrieve |

---

### `list_service_change_events`

List all change events for a specific service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_id` | `string` | Yes | The ID of the service |
| `query_model` | `ChangeEventQuery` | No | Query parameters for filtering change events |

**Example prompt:**

> "What changes were made to the payment-service in the last week?"

---

### `list_incident_change_events`

List change events related to a specific incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident |
| `limit` | `integer` | No | Maximum number of results to return |

**Example prompt:**

> "What change events are related to incident P123456?"
