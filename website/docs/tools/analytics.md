---
sidebar_position: 16
---

# Analytics

PagerDuty Analytics tools provide pre-aggregated incident and responder metrics powered by the PagerDuty Analytics engine. These tools are useful for measuring team performance, responder workload, and service health over a time range.

## Tools

### `get_responder_metrics`

Get per-responder aggregate metrics grouped by team, including on-call hours, interruption counts (business, off-hours, sleep), and engaged time.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_range_start` | `string` | Yes | ISO 8601 DateTime. Incidents with created_at before this value are omitted. |
| `date_range_end` | `string` | Yes | ISO 8601 DateTime. Incidents with created_at >= this value are omitted. |
| `team_ids` | `string[]` | No | Only incidents related to these teams will be included. |
| `responder_ids` | `string[]` | No | Only incidents related to these responders will be included. |
| `urgency` | `string` | No | Filter by urgency: `"high"` or `"low"`. |
| `time_zone` | `string` | No | The time zone to use for results and grouping (e.g. `"America/New_York"`). |
| `order` | `string` | No | Sort order: `"asc"` or `"desc"`. |
| `order_by` | `string` | No | Field to sort results by. |

**Example prompt:**

> "Show me on-call hours and interruption counts for all responders on the platform team last month"

---

### `get_incident_metrics_by_service`

Get aggregated incident metrics per service including MTTA, MTTR, escalation counts, and uptime percentage.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `created_at_start` | `string` | Yes | ISO 8601 DateTime. Incidents created before this are omitted. |
| `created_at_end` | `string` | Yes | ISO 8601 DateTime. Incidents created on/after this are omitted. |
| `team_ids` | `string[]` | No | Only incidents related to these teams will be included. |
| `service_ids` | `string[]` | No | Only incidents related to these services will be included. |
| `urgency` | `string` | No | Filter by urgency: `"high"` or `"low"`. |
| `time_zone` | `string` | No | The time zone for results (e.g. `"America/New_York"`). |
| `order` | `string` | No | Sort order: `"asc"` or `"desc"`. |
| `order_by` | `string` | No | Field to sort results by. |

**Example prompt:**

> "Which services had the worst MTTR last quarter?"

---

### `get_incident_metrics_by_team`

Get aggregated incident metrics per team including MTTA, MTTR, and interruption breakdowns. Supports time-series aggregation by day, week, or month.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `created_at_start` | `string` | Yes | ISO 8601 DateTime. Incidents created before this are omitted. |
| `created_at_end` | `string` | Yes | ISO 8601 DateTime. Incidents created on/after this are omitted. |
| `team_ids` | `string[]` | No | Only incidents related to these teams will be included. |
| `service_ids` | `string[]` | No | Only incidents related to these services will be included. |
| `urgency` | `string` | No | Filter by urgency: `"high"` or `"low"`. |
| `time_zone` | `string` | No | The time zone for results (e.g. `"America/New_York"`). |
| `order` | `string` | No | Sort order: `"asc"` or `"desc"`. |
| `order_by` | `string` | No | Field to sort results by. |
| `aggregate_unit` | `string` | No | Time unit to aggregate metrics by: `"day"`, `"week"`, or `"month"`. If omitted, returns a single all-period row. |

**Example prompt:**

> "Show me weekly incident volume by team for Q1"

---

### `get_responder_load_metrics`

Get per-responder load metrics including on-call hours, incident count, acknowledgment count, and sleep-hour interruptions across all teams.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_range_start` | `string` | Yes | ISO 8601 DateTime. Incidents with created_at before this value are omitted. |
| `date_range_end` | `string` | Yes | ISO 8601 DateTime. Incidents with created_at >= this value are omitted. |
| `team_ids` | `string[]` | No | Only incidents related to these teams will be included. |
| `urgency` | `string` | No | Filter by urgency: `"high"` or `"low"`. |
| `time_zone` | `string` | No | The time zone for results (e.g. `"America/New_York"`). |
| `order` | `string` | No | Sort order: `"asc"` or `"desc"`. |
| `order_by` | `string` | No | Field to sort results by. |

**Example prompt:**

> "Who has the highest on-call burden across all teams this month?"

---

### `get_incident_metrics_all`

Get full-period aggregated incident metrics including percentile distributions (P50, P75, P90, P95) for acknowledgment and resolution times. These percentile fields are only available from this endpoint.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `created_at_start` | `string` | Yes | ISO 8601 DateTime. Incidents created before this are omitted. |
| `created_at_end` | `string` | Yes | ISO 8601 DateTime. Incidents created on/after this are omitted. |
| `team_ids` | `string[]` | No | Only incidents related to these teams will be included. |
| `service_ids` | `string[]` | No | Only incidents related to these services will be included. |
| `urgency` | `string` | No | Filter by urgency: `"high"` or `"low"`. |
| `time_zone` | `string` | No | The time zone for results (e.g. `"America/New_York"`). |
| `order` | `string` | No | Sort order: `"asc"` or `"desc"`. |
| `order_by` | `string` | No | Field to sort results by. |

**Example prompt:**

> "What is the P95 MTTR across the entire account for the last 90 days?"
