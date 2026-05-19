---
sidebar_position: 19
---

# On-Call Compensation

The on-call compensation tool computes a full compensation and compliance report server-side, returning structured data that agents can query, filter, and reason over directly — without opening a browser. It replicates the computation pipeline of the [On-Call Compensation Report](../experimental/oncall-compensation) MCP App.

## Tools

### `get_oncall_compensation_report`

Generate a per-user on-call compensation and compliance report for a given date range. Returns scheduled hours, interruption counts broken down by business/off/sleep hours, compliance status, fairness metrics, and optional forward-mode projections.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `OncallCompensationRequest` | Yes | Report parameters (see below) |

#### `OncallCompensationRequest` fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `since` | `string` | Yes | Start of reporting period in ISO 8601 format (e.g. `2026-01-01T00:00:00Z`). Inclusive. Maximum recommended range: 90 days. |
| `until` | `string` | Yes | End of reporting period in ISO 8601 format (e.g. `2026-01-31T23:59:59Z`). Exclusive. |
| `team_ids` | `list[string]` | No | Restrict report to specific team IDs. Leave null for all teams. |
| `escalation_policy_id` | `string` | No | Restrict report to users in a specific escalation policy. |
| `compliance_template` | `string` | No | Pre-built compliance rule set: `"emea"` (EU Working Time Directive), `"us"` (40h/week standard), or `"none"` (default, no compliance limits). |
| `forward` | `boolean` | No | If `true`, run in forward-estimation mode — projects on-call hours from scheduled shifts without querying Analytics (useful for future date ranges). Interruptions and incident counts will be 0. |

**Example prompts:**

> "Generate an on-call compensation report for all teams for January 2026"

> "Show me the on-call burden report for the SRE team from 2026-03-01 to 2026-03-31"

> "Project on-call hours for next month across all schedules"

> "Run a compensation report for escalation policy PXXXXXX with EMEA compliance rules"
