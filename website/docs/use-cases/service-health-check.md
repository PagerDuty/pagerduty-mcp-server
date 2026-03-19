---
sidebar_position: 4
---

# Service Health Check

**Scenario:** A team wants a quick, AI-generated health summary for their services — recent incidents, change activity, and log entry anomalies — without navigating multiple PagerDuty views.

**Mode:** Read-only

## Tools involved

| Tool | Purpose |
|------|---------|
| `list_services` | Enumerate services for a team |
| `get_service` | Get configuration details for a specific service |
| `list_incidents` | Find recent incidents per service |
| `list_change_events` | Identify recent deployments or config changes |
| `list_service_change_events` | Scope change events to a specific service |
| `list_log_entries` | Review the event audit trail |

## Example prompts

```
Give me a health summary for all services owned by the platform team.
```

```
What incidents has the checkout-api service had in the last 7 days?
Were any correlated with change events?
```

```
Show me all change events for the payments service in the last 24 hours.
```

```
Are there any services with open incidents that also had a deployment
in the last hour?
```

## Workflow

1. List services filtered by team
2. For each service, pull recent incidents and change events in parallel
3. Ask the AI to correlate incidents with changes (e.g. did a deploy precede the incident?)
4. Generate a health report per service or per team

## Tips

- This pairs well as a daily standup input — ask for a health check at the start of every morning
- Scope to a single team with `list_services` + team filter to avoid information overload
- Use `list_log_entries` when you need the full audit trail beyond incidents and changes
