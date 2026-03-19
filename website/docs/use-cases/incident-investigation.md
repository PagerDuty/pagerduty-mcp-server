---
sidebar_position: 2
---

# Incident Investigation

**Scenario:** An alert fires and an engineer needs to quickly understand what's happening — the scope of impact, related alerts, recent changes, and the history of notes left by the on-call team.

**Mode:** Read-only (no `--enable-write-tools` needed)

## Tools involved

| Tool | Purpose |
|------|---------|
| `list_incidents` | Find the active incident(s) |
| `get_incident` | Pull full incident details |
| `list_alerts_from_incident` | See every alert grouped into the incident |
| `list_incident_notes` | Read the timeline of responder notes |
| `list_incident_change_events` | Correlate recent deploys or config changes |
| `get_past_incidents` | Find similar incidents from the last 6 months |
| `get_related_incidents` | Identify other services currently impacted |

## Example prompts

```
What open high-urgency incidents do we have right now?
```

```
Give me a full summary of incident P123456 — what triggered it,
which alerts fired, what notes have been added, and any related change events.
```

```
Have we seen a similar incident to P123456 in the past 6 months?
What was the resolution?
```

```
Are there any other services currently impacted alongside the incident
on the payments service?
```

## Workflow

1. Start broad — ask for all open incidents filtered by urgency or service
2. Drill into the specific incident to get alerts and notes
3. Pull change events to correlate with the trigger time
4. Check past and related incidents for pattern recognition

## Tips

- Combine with [Tool Filtering](../configuration/tool-filtering) to expose only the investigation tools, keeping the AI focused on diagnostics rather than remediation
- Pair `get_past_incidents` and `get_related_incidents` with the Event Intelligence package for richer pattern data
