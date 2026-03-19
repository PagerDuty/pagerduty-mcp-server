---
sidebar_position: 3
---

# Alerts

Alerts are individual triggered events that are grouped into incidents. These tools let you inspect alerts within a given incident.

## Tools

### `list_alerts_from_incident`

List alerts for a specific incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident |
| `query_model` | `AlertQuery` | No | Query parameters for pagination |

**Example prompt:**

> "Show me all alerts for incident P123456"

---

### `get_alert_from_incident`

Get a specific alert from an incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident |
| `alert_id` | `string` | Yes | The ID of the alert |

**Example prompt:**

> "Get alert PA00001 from incident P123456"
