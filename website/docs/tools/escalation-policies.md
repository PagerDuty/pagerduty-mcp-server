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

---

### `create_escalation_policy` *(write)*

Create a new escalation policy.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `escalation_policy` | `EscalationPolicyCreate` | Yes | Policy data: `name`, `escalation_rules` (ordered list of rules), optional `description`, `num_loops`, `on_call_handoff_notifications` |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create an escalation policy named 'Platform On-Call' with a 5-minute escalation rule to the Platform schedule"

---

### `update_escalation_policy` *(write)*

Update an existing escalation policy.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | `string` | Yes | The ID of the escalation policy to update |
| `escalation_policy` | `EscalationPolicyCreate` | Yes | The updated policy data |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `delete_escalation_policy` *(write)*

Delete an escalation policy.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | `string` | Yes | The ID of the escalation policy to delete |

:::note
Requires `--enable-write-tools` flag.
:::
