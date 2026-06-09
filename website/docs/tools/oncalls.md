---
sidebar_position: 11
---

# On-Call

The on-call domain provides a single tool for querying current on-call assignments across all schedules and escalation policies.

## Tools

### `list_oncalls`

List on-call schedules with optional filtering. Returns who is currently on-call across your account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `OncallQuery` | No | Optional filtering parameters (schedule IDs, escalation policy IDs, user IDs, time range) |

**Example prompts:**

> "Who is currently on-call?"

> "Who is on-call for the payments escalation policy?"

> "List all on-call assignments for schedule PXXXXXX right now"
