---
sidebar_position: 13
---

# Escalation Policies

Escalation policies define the sequence of steps PagerDuty follows when notifying responders about an incident. They connect services to on-call schedules and individual users.

## Tools

### `list_escalation_policies`

List escalation policies with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `EscalationPolicyQuery` | No | Optional filtering parameters (name, team, pagination) |

**Example prompts:**

> "List all escalation policies"

> "Show escalation policies for the infrastructure team"

---

### `get_escalation_policy`

Get a specific escalation policy by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | `string` | Yes | The ID of the escalation policy to retrieve |

**Example prompt:**

> "Get the details of escalation policy PXXXXXX"
