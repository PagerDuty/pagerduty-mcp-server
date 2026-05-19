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
| `request` | `GetResponderMetricsRequest` | Yes | Filters including required `filters.date_range_start` and `filters.date_range_end` (ISO 8601), optional `filters.team_ids`, `filters.responder_ids`, `filters.urgency`, `time_zone`, `order`, `order_by` |

**Example prompt:**

> "Show me on-call hours and interruption counts for all responders on the platform team last month"

---

### `get_incident_metrics_by_service`

Get aggregated incident metrics per service including MTTA, MTTR, escalation counts, and uptime percentage.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetIncidentMetricsByServiceRequest` | Yes | Filters including required `filters.created_at_start` and `filters.created_at_end` (ISO 8601), optional `filters.team_ids`, `filters.service_ids`, `filters.urgency`, `time_zone`, `order`, `order_by` |

**Example prompt:**

> "Which services had the worst MTTR last quarter?"

---

### `get_incident_metrics_by_team`

Get aggregated incident metrics per team including MTTA, MTTR, and interruption breakdowns. Supports time-series aggregation by day, week, or month.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetIncidentMetricsByTeamRequest` | Yes | Filters including required `filters.created_at_start` and `filters.created_at_end` (ISO 8601), optional `filters.team_ids`, `filters.service_ids`, `filters.urgency`, `time_zone`, `order`, `order_by`, `aggregate_unit` (`"day"`, `"week"`, `"month"`) |

**Example prompt:**

> "Show me weekly incident volume by team for Q1"

---

### `get_responder_load_metrics`

Get per-responder load metrics including on-call hours, incident count, acknowledgment count, and sleep-hour interruptions across all teams.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetResponderLoadMetricsRequest` | Yes | Filters including required `filters.date_range_start` and `filters.date_range_end` (ISO 8601), optional `filters.team_ids`, `filters.urgency`, `time_zone`, `order`, `order_by` |

**Example prompt:**

> "Who has the highest on-call burden across all teams this month?"

---

### `get_incident_metrics_all`

Get full-period aggregated incident metrics including percentile distributions (P50, P75, P90, P95) for acknowledgment and resolution times. These percentile fields are only available from this endpoint.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetIncidentMetricsAllRequest` | Yes | Filters including required `filters.created_at_start` and `filters.created_at_end` (ISO 8601), optional `filters.team_ids`, `filters.service_ids`, `filters.urgency`, `time_zone`, `order`, `order_by` |

**Example prompt:**

> "What is the P95 MTTR across the entire account for the last 90 days?"
