---
sidebar_position: 19
---

# On-Call Compensation

The on-call compensation tool computes a detailed compensation and burden report for all responders in a given time window. It uses PagerDuty Analytics, on-call schedules, and incident data to produce a rich dataset suitable for payroll, compliance, and fairness analysis.

## Tools

### `get_oncall_compensation_report`

Generate a full on-call compensation report for a time period. The report includes per-responder on-call hours, outside-hours breakdowns (evenings, weekends, sleep), incident counts by urgency, estimated compensation amounts, and optional compliance flag checks (EU Working Time Directive, US overtime, or custom thresholds).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `OncallCompensationRequest` | Yes | Report parameters — see fields below |

**`OncallCompensationRequest` fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `since` | `string` | Yes | Start of reporting period (ISO 8601, e.g. `"2026-01-01T00:00:00Z"`). Maximum recommended range: 90 days. |
| `until` | `string` | Yes | End of reporting period (ISO 8601, exclusive). |
| `team_ids` | `list[string]` | No | Filter to specific teams. If omitted, all teams are included. |
| `escalation_policy_ids` | `list[string]` | No | Filter to specific escalation policies. |
| `hourly_rate` | `float` | No | Flat hourly rate (USD) applied to all on-call hours for cost estimation. |
| `outside_hours_multiplier` | `float` | No | Multiplier applied to evening/weekend/sleep hours (e.g. `1.5` for time-and-a-half). |
| `compliance_template` | `string` | No | Compliance ruleset to apply: `"emea"` (EU Working Time Directive, 48 h/week avg), `"us"` (40 h/week), or `"none"` (no limits). |
| `business_hours_start` | `integer` | No | Start of business hours (24-hour clock, default `8`). |
| `business_hours_end` | `integer` | No | End of business hours (24-hour clock, default `18`). |
| `currency` | `string` | No | Currency symbol for display (default `"USD"`). |
| `forward_mode` | `boolean` | No | If `true`, returns a forward-looking projection based on current schedule rather than historical actuals. |

**Example prompts:**

> "Generate an on-call compensation report for the platform team for January 2026, using a $50/hour rate with 1.5x for outside-hours shifts"

> "Check if any responders are approaching EU Working Time Directive limits this month"

> "Who carried the most on-call burden last quarter and what would their estimated compensation be?"

> "Show me a breakdown of weeknight vs. weekend on-call hours for all responders"
