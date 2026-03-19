---
sidebar_position: 5
---

# Incidents

Incidents are the core of PagerDuty — they represent service disruptions that require attention. This domain has the largest tool set with 10 tools covering listing, investigation, creation, and management.

## Tools

### `list_incidents`

List incidents with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `IncidentQuery` | No | Optional filtering parameters (status, urgency, service, team, date range, etc.) |

**Example prompts:**

> "List all open high-urgency incidents"

> "Show me incidents from the last hour"

---

### `get_incident`

Get a specific incident by ID or incident number.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID or number of the incident to retrieve |
| `query_model` | `GetIncidentQuery` | No | Optional query parameters for additional information to include |

**Example prompt:**

> "Get details for incident P123456"

---

### `get_outlier_incident`

Get outlier incident analysis for a given incident on its service. Returns incidents that deviate from expected patterns for the same service.

:::info
This feature requires the Event Intelligence package or Digital Operations plan.
:::

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident to get outlier information for |
| `query_model` | `OutlierIncidentQuery` | No | Query parameters including date range and additional details |

---

### `get_past_incidents`

Get past incidents related to a specific incident. Returns incidents within the past 6 months with similar metadata generated on the same service. Returns up to 50 past incidents by default.

:::info
This feature requires the Event Intelligence package or Digital Operations plan.
:::

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident to get past incidents for |
| `query_model` | `PastIncidentsQuery` | No | Query parameters including limit and total flag |

---

### `get_related_incidents`

Get related incidents for a specific incident. Returns the 20 most recent related incidents that are impacting other responders and services.

:::info
This feature requires the Event Intelligence package or Digital Operations plan.
:::

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident to get related incidents for |
| `query_model` | `RelatedIncidentsQuery` | No | Query parameters including additional details |

---

### `list_incident_notes`

List all notes for a specific incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident to retrieve notes from |

---

### `create_incident` *(write)*

Create a new incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `create_model` | `IncidentCreateRequest` | Yes | The incident creation request (title, service, urgency, etc.) |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create a high-urgency incident titled 'Payment gateway down' on the payments service"

---

### `manage_incidents` *(write)*

Manage one or more incidents by changing status, urgency, assignment, or escalation level. Use this tool for bulk updates.

The `manage_request` model accepts these flat fields:
- `incident_ids` — list of incident IDs to update
- `status` — new status (e.g., `acknowledged`, `resolved`)
- `urgency` — `high` or `low`
- `assignment` — `UserReference` with `id` field
- `escalation_level` — integer

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `manage_request` | `IncidentManageRequest` | Yes | Incident IDs and fields to update |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Acknowledge all incidents assigned to user PXXXXXX"

---

### `add_responders` *(write)*

Add responders to an incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident to add responders to |
| `request` | `IncidentResponderRequest` | Yes | Responder request data containing user IDs and optional message |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `add_note_to_incident` *(write)*

Add a note to an incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `incident_id` | `string` | Yes | The ID of the incident to add a note to |
| `note` | `string` | Yes | The note text to be added |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Add a note to incident P123456 saying 'Database failover initiated'"
