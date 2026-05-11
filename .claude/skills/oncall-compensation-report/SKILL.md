---
name: oncall-compensation-report
description: Use when answering questions about on-call hours, compensation costs, burden distribution, compliance limits, or fairness across responders. Covers queries like "who was on call most last month", "estimate on-call pay for my team", "flag anyone approaching overtime limits", "show weekend burden breakdown", or "check EU Working Time Directive compliance".
---

# On-Call Compensation Report — Agentic Usage Guide

## Two modes: UI + Agentic

The on-call compensation feature works in both modes simultaneously:

| Mode | How to invoke | Use for |
|---|---|---|
| **Interactive UI** | `oncall_compensation` tool | Visual exploration, custom pay config, export |
| **Agentic report** | `get_oncall_compensation_report` tool | Answering questions, comparisons, compliance checks, payroll exports |

Both use the same underlying data. Use the UI when the user wants to explore interactively. Use the agentic tool when the user asks a specific question you can answer with structured data.

---

## Config-gathering workflow

Before calling `get_oncall_compensation_report`, collect the minimal context needed. Ask only what you don't know.

### Step 1 — Date range (always required)
- "What period?" → `since` / `until`
- Default if unspecified: last 30 days

### Step 2 — Scope (usually optional)
- "Which team or escalation policy?" → call `list_teams` or `list_escalation_policies` to get IDs
- Leave null for org-wide

### Step 3 — Timezone (important for outside-hours accuracy)
- "Where is the team based?" → map to IANA timezone
- Common mappings: US East → `America/New_York`, US West → `America/Los_Angeles`, UK → `Europe/London`, DACH → `Europe/Berlin`, India → `Asia/Kolkata`
- **Default is UTC** — always set this for meaningful outside-hours numbers

### Step 4 — What kind of analysis?

| User intent | What to configure |
|---|---|
| "Who worked most / burden report" | Just date + timezone. No pay or compliance needed. |
| "Estimate compensation / pay costs" | Ask for `l1_rate_per_hour`. Optionally `l2_plus_rate_per_hour` and multipliers. |
| "Check compliance / overtime limits" | Ask region or use `compliance_template`: `emea` or `us`. |
| "Holiday pay calculation" | Ask for holiday dates as `YYYY-MM-DD` list. |
| "Custom business hours" | Ask for start/end hour and work days. |

**Never ask for all config upfront.** Lead with what you know. Call the tool with defaults and refine.

---

## Compliance templates

Use `compliance_template` to pre-configure legal/policy limits. The tool auto-flags violations.

| Template | Use for | Limits |
|---|---|---|
| `"emea"` | EU teams (GDPR WTD) | 192h/4wk cap, 80h outside cap, max 6 consec. days, 11h rest |
| `"us"` | US teams | 160h/4wk cap, 60h outside cap, max 7 consec. days, 8h rest |
| `"none"` | Burden/pay only (default) | No compliance checks |

You can mix a template with custom overrides:
```json
{
  "compliance_template": "emea",
  "min_rest_hours": 12
}
```

---

## Key parameters

### Required
- `since` / `until` — ISO 8601. Use `T00:00:00Z` / `T23:59:59Z`. Max recommended: 90 days.

### Scope
- `team_ids` — list of team IDs (from `list_teams`)
- `escalation_policy_id` — single EP ID (from `list_escalation_policies`)

### Compliance
- `compliance_template` — `"emea"` | `"us"` | `"none"` (default)
- `hours_cap`, `outside_hours_cap`, `max_consecutive_days`, `max_consecutive_hours`, `min_rest_hours` — override individual limits (0 = use template)

### Business hours (affects outside-hours breakdown)
- `timezone` — IANA string. **Always set this.** Default: `"UTC"`
- `biz_start_hour` / `biz_end_hour` — local hours, default `9` / `18`
- `work_days` — ISO weekday numbers (1=Mon … 7=Sun), default `[1,2,3,4,5]`
- `holidays` — list of `"YYYY-MM-DD"` holiday dates

### Pay estimation (all optional, default 0 = skip)
- `l1_rate_per_hour` — base hourly rate for L1 on-call
- `l2_plus_rate_per_hour` — rate for L2+ (backup) shifts
- `off_hours_multiplier` — weekday OOH multiplier (default 1.5×)
- `weekend_multiplier` — weekend multiplier (default 2.0×)
- `holiday_multiplier` — holiday multiplier (default 2.5×)

### Output control
- `min_scheduled_hours` — exclude users below this threshold (e.g. `1.0` removes noise)
- `include_incidents` — include per-user incident list (larger response)
- `include_directly_added` — include EP-layer shifts not backed by a schedule

---

## Response fields to reason over

### Top-level
- `total_users`, `total_scheduled_hours`, `total_outside_hours`, `total_estimated_pay`
- `compliance_violations` — count of users with status `"over"`
- `compliance_near_limit` — count of users approaching a limit
- `team_summary[]` — aggregated per team

### Per user (`users[]`, sorted by `scheduled_hours` descending)
| Field | What it means |
|---|---|
| `scheduled_hours` | Total on-call hours (Analytics — authoritative, overlap-deduped) |
| `outside_hours` | All hours outside business hours (weeknight + weekend + holiday) |
| `weekend_hours` | Hours on weekend calendar days |
| `holiday_hours` | Hours on configured holiday dates |
| `weeknight_hours` | Weekday hours outside biz_start–biz_end |
| `weekend_period_count` | Distinct weekends touched |
| `total_interruptions` | All interruptions (business + off + sleep) |
| `sleep_hour_interruptions` | Interruptions 10pm–8am (PD native, user's PD timezone) |
| `max_consecutive_on_call_hours` | Longest single unbroken on-call shift |
| `max_consecutive_on_call_days` | Longest run of consecutive days on call |
| `min_rest_hours` | Shortest gap between shifts (999 = no consecutive shifts found) |
| `estimated_pay` | Estimated pay (0 if `l1_rate_per_hour` not set) |
| `compliance_status` | `"ok"` / `"near"` / `"over"` |
| `compliance_flags` | Human-readable list, e.g. `["over:hours_cap (200.5 / 192 limit)"]` |

---

## Common recipes

### Burden report — who worked most last month
```json
{
  "since": "2026-04-01T00:00:00Z",
  "until": "2026-04-30T23:59:59Z",
  "timezone": "America/Chicago",
  "min_scheduled_hours": 1.0
}
```
→ Summarize `users[0..4]` by `scheduled_hours`, `outside_hours`, `total_interruptions`

### Pay estimate for a team
1. `list_teams` → get team ID
2. Ask user for L1 rate, whether to apply multipliers, and any holidays
```json
{
  "since": "2026-04-01T00:00:00Z",
  "until": "2026-04-30T23:59:59Z",
  "team_ids": ["TABC123"],
  "timezone": "Europe/London",
  "l1_rate_per_hour": 25.0,
  "l2_plus_rate_per_hour": 15.0,
  "holiday_multiplier": 3.0,
  "holidays": ["2026-04-18", "2026-04-21"]
}
```
→ Report `total_estimated_pay` and per-user `estimated_pay`

### EU WTD compliance check (4-week period)
```json
{
  "since": "2026-04-01T00:00:00Z",
  "until": "2026-04-28T23:59:59Z",
  "compliance_template": "emea",
  "timezone": "Europe/Berlin"
}
```
→ Check `compliance_violations`. For each flagged user, list `compliance_flags`.

### Weekend fairness audit
```json
{
  "since": "2026-01-01T00:00:00Z",
  "until": "2026-03-31T23:59:59Z",
  "timezone": "America/Los_Angeles"
}
```
→ Sort `users` by `weekend_period_count` descending. Flag users with more than 1.5× the team average.

### Sleep-hour fatigue report
```json
{ "since": "...", "until": "...", "timezone": "America/New_York" }
```
→ Sort by `sleep_hour_interruptions`. Flag ≥5 as high risk, ≥2 as medium risk.

---

## Gotchas

1. **Analytics lag** — `get_responder_metrics` data can lag up to 24h. For shifts happening today, use `list_oncalls` directly.
2. **`until` is exclusive** — always use `T23:59:59Z` (not `T00:00:00Z`) for the last day of the period.
3. **Timezone matters** — without it, all outside-hours math uses UTC. A weekend at UTC midnight may be a Friday evening in New York.
4. **`sleep_hour_interruptions`** — uses PagerDuty's own definition (10pm–8am in the user's PD account timezone), not the `timezone` parameter.
5. **`min_rest_hours: 999`** — means no consecutive shifts were found in the window; not a violation.
6. **Pay is scheduled on-call time**, not incident response time. `incident_hours` (engaged time) is reported separately.
7. **`min_scheduled_hours: 1.0`** — recommended for org-wide queries to exclude users briefly added to policies.
