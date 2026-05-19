---
sidebar_position: 16
---

# Analytics

Analytics tools expose PagerDuty's pre-aggregated metrics engine. Use these tools instead of `list_incidents` when you need MTTA, MTTR, on-call hours, or interruption counts — the data is computed server-side and far more efficient than page-by-page incident iteration.

## Tools

### `get_responder_metrics`

Get per-responder on-call metrics aggregated by team from PagerDuty Analytics. Returns on-call seconds, interruption counts broken down by business hours / off hours / sleep hours, engaged time, and incident counts for a given date range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetResponderMetricsRequest` | Yes | Filters object with `date_range_start` and `date_range_end` (ISO 8601). Optional `team_ids`, `responder_ids`, `urgency`, `time_zone`, `order`, `order_by`. |

**Example prompts:**

> "Show me on-call hours and interruption counts for all responders last month"

> "Get responder metrics for team PXXXXXX between 2026-01-01 and 2026-02-01"

---

### `get_incident_metrics_by_service`

Get aggregated incident metrics per service. Returns service-level MTTA, mean MTTR, escalation counts, incident volume, and uptime percentage for the requested period.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetIncidentMetricsByServiceRequest` | Yes | Filters object with `created_at_start` and `created_at_end` (ISO 8601). Optional `team_ids`, `service_ids`, `urgency`, `time_zone`, `order`, `order_by`. |

**Example prompts:**

> "Which services had the highest MTTR last quarter?"

> "Show incident counts and uptime per service for the infrastructure team in January"

---

### `get_incident_metrics_by_team`

Get aggregated incident metrics per team. Returns team-level MTTA, mean MTTR, escalation counts, incident volume, and uptime percentage. Supports optional time-bucketing by day, week, or month.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetIncidentMetricsByTeamRequest` | Yes | Filters object with `created_at_start` and `created_at_end` (ISO 8601). Optional `team_ids`, `service_ids`, `urgency`, `time_zone`, `order`, `order_by`, `aggregate_unit` (`"day"`, `"week"`, or `"month"`). |

**Example prompts:**

> "Compare MTTA across all teams for Q1 2026"

> "Show weekly incident volume per team for the last 3 months"

---

### `get_responder_load_metrics`

Get aggregated load metrics per responder across all teams. Returns per-responder on-call hours, incident count, acknowledgment count, sleep-hour interruptions, and engaged time.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetResponderLoadMetricsRequest` | Yes | Filters object with `date_range_start` and `date_range_end` (ISO 8601). Optional `team_ids`, `urgency`, `time_zone`, `order`, `order_by`. |

**Example prompts:**

> "Who had the most on-call hours across the entire organization last month?"

> "Show me responder load metrics for the month of March"

---

### `get_incident_metrics_all`

Get full-period aggregated incident metrics rolled up across the entire account. Returns total incident count, MTTA, MTTR, and percentile distributions (P50, P75, P90, P95) for acknowledge and resolve times.

:::info
Percentile distributions (P50, P75, P90, P95) are **only** available from this endpoint — the per-team and per-service grouped endpoints do not return them.
:::

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `GetIncidentMetricsAllRequest` | Yes | Filters object with `created_at_start` and `created_at_end` (ISO 8601). Optional `team_ids`, `service_ids`, `urgency`, `time_zone`. |

**Example prompts:**

> "What's the P95 resolution time for all high-urgency incidents this quarter?"

> "Show me overall MTTA and MTTR for the entire account in January"
