---
sidebar_position: 3
---

# On-Call Handoff

**Scenario:** At the end of a shift, the outgoing on-call engineer wants to brief the incoming engineer on the current state — who is on-call, what's open, and what to watch.

**Mode:** Read-only

## Tools involved

| Tool | Purpose |
|------|---------|
| `get_user_data` | Confirm current user identity |
| `list_oncalls` | See who is currently on-call across all schedules |
| `list_schedules` | Review coverage for the next 24–48 hours |
| `list_incidents` | Summarize open incidents to hand off |
| `list_incident_notes` | Pull context and last actions on open incidents |

## Example prompts

```
Who is currently on-call for each of our escalation policies?
```

```
Summarize all open incidents I should be aware of for handoff —
include urgency, current status, and the last note on each.
```

```
Is there any gap in on-call coverage for the platform schedule
over the next 48 hours?
```

```
Generate a handoff briefing for the incoming on-call: open incidents,
their current status, and what actions have been taken so far.
```

## Workflow

1. Ask for the current on-call roster across all relevant escalation policies
2. Pull all open or acknowledged incidents with their last notes
3. Check schedule coverage for the next shift window
4. Have the AI draft a written handoff summary you can paste into Slack or your team's handoff doc

## Tips

- Use [Tool Filtering](../configuration/tool-filtering) with an allow list of `list_oncalls`, `list_schedules`, `list_incidents`, `list_incident_notes`, `get_user_data` to keep the AI scoped to handoff tasks only
- Ask for the output in a specific format (Markdown table, Slack message, bullet list) to drop it directly into your communication channel
