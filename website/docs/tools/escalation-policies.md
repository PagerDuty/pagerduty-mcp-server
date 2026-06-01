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
| `escalation_policy` | `EscalationPolicyCreate` | Yes | Policy data including `name`, `escalation_rules` (ordered list of targets and delays), optional `description`, `num_loops`, `on_call_handoff_notifications`, and `teams` |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create an escalation policy called 'Platform On-Call' with a 5-minute delay to user PXXXXXX, then escalate to schedule PXXXXXX"

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

**Example prompt:**

> "Update escalation policy PXXXXXX to add a second escalation step to the platform team schedule"

---

### `delete_escalation_policy` *(write)*

Delete an escalation policy. The policy must not be in use by any services.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | `string` | Yes | The ID of the escalation policy to delete |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Delete escalation policy PXXXXXX"
