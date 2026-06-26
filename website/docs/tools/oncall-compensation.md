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
| `escalation_policy_id` | `string` | No | Filter to users in a specific escalation policy. |
| `compliance_template` | `string` | No | Compliance ruleset to apply: `"emea"` (EU Working Time Directive), `"us"` (US defaults), or `"none"` (no limits, default). |
| `hours_cap` | `float` | No | Override: max scheduled hours allowed per period. `0` = use template value (default `0.0`). |
| `outside_hours_cap` | `float` | No | Override: max outside-business-hours allowed per period. `0` = use template value (default `0.0`). |
| `max_consecutive_days` | `integer` | No | Override: max consecutive on-call days. `0` = use template value (default `0`). |
| `max_consecutive_hours` | `float` | No | Override: configurable cap on consecutive on-call hours. `0` = use template value (default `0.0`). |
| `min_rest_hours` | `float` | No | Override: minimum rest hours between on-call periods. `0` = use template value (default `0.0`). |
| `biz_start_hour` | `integer` | No | Start of business hours (24-hour clock, default `9`). |
| `biz_end_hour` | `integer` | No | End of business hours (24-hour clock, default `18`). |
| `timezone` | `string` | No | Timezone for outside-hours calculations (default `"UTC"`). |
| `work_days` | `list[integer]` | No | ISO weekday numbers considered work days (default `[1, 2, 3, 4, 5]` = Mon–Fri). |
| `holidays` | `list[string]` | No | List of holiday dates in `"YYYY-MM-DD"` format for holiday pay calculations. |
| `l1_rate_per_hour` | `float` | No | Hourly rate (USD) for level-1 on-call shifts (default `0.0`). |
| `l2_plus_rate_per_hour` | `float` | No | Hourly rate (USD) for level-2+ on-call shifts (default `0.0`). |
| `off_hours_multiplier` | `float` | No | Multiplier applied to off-hours (evening) shifts (default `1.5`). |
| `weekend_multiplier` | `float` | No | Multiplier applied to weekend shifts (default `2.0`). |
| `holiday_multiplier` | `float` | No | Multiplier applied to holiday shifts (default `2.5`). |
| `include_incidents` | `boolean` | No | If `true`, fetches incident data and includes urgency breakdown per user (default `false`). |
| `include_directly_added` | `boolean` | No | If `true`, includes users added directly to an escalation policy without a schedule (default `false`). |
| `min_scheduled_hours` | `float` | No | Exclude users with fewer than this many scheduled hours from the report (default `0.0`). |
| `forward` | `boolean` | No | If `true`, returns a forward-looking projection based on current schedules rather than historical actuals (default `false`). |

**Example prompts:**

> "Generate an on-call compensation report for the platform team for January 2026, using a $50/hour rate with 1.5x for outside-hours shifts"

> "Check if any responders are approaching EU Working Time Directive limits this month"

> "Who carried the most on-call burden last quarter and what would their estimated compensation be?"

> "Show me a breakdown of weeknight vs. weekend on-call hours for all responders"
