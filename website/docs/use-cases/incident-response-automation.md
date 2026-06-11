---
sidebar_position: 5
---

# Incident Response Automation

**Scenario:** When a known failure pattern is detected, an engineer uses the AI to execute a standard response playbook — creating the incident, adding responders, triggering the relevant workflow, and leaving structured notes — all through conversation.

**Mode:** Write (`--enable-write-tools` required)

:::caution
This use case requires write tools. Ensure you understand the actions being taken before confirming any AI-suggested operations that create or modify PagerDuty resources.
:::

## Tools involved

| Tool | Purpose |
|------|---------|
| `create_incident` | Open a new incident |
| `manage_incidents` | Acknowledge or escalate |
| `add_responders` | Page the right people |
| `add_note_to_incident` | Log actions and context |
| `start_incident_workflow` | Trigger a pre-built response workflow |
| `list_incident_workflows` | Find the right workflow to trigger |
| `list_escalation_policies` | Identify the correct escalation path |
| `list_users` | Find responder user IDs |

## Example prompts

```
Create a high-urgency incident titled "Database primary down" on the
database-primary service and assign it to the database escalation policy.
```

```
Add a note to incident P123456: "Failover initiated to replica db-west-2.
ETA 5 minutes. Monitoring replication lag."
```

```
Find the major incident response workflow and trigger it for incident P123456.
```

```
Add the database on-call engineer and the SRE lead as responders to P123456
with the message "Database failover in progress — need DB expert and SRE coverage."
```

## Workflow

1. Identify the incident type and affected service
2. Create the incident with correct title, service, and escalation policy
3. Add the relevant responders with context in the message
4. Trigger the incident workflow for your team's standard runbook
5. Leave structured notes as actions are taken to maintain a clear timeline

## Tips

- Use [Tool Filtering](../configuration/tool-filtering) with a focused allow list for response workflows — e.g. only expose `create_incident`, `manage_incidents`, `add_responders`, `add_note_to_incident` to prevent the AI from touching unrelated resources
- Always review what the AI is about to do before confirming — especially `manage_incidents` which can bulk-update multiple incidents at once
- Combine with read tools to let the AI look up user IDs and policy IDs rather than hardcoding them in prompts
