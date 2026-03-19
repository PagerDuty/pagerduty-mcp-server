---
sidebar_position: 9
---

# Users

User tools let you retrieve information about the currently authenticated user and list all users in the account.

## Tools

### `get_user_data`

Get the current authenticated user's data, including name, role, ID, summary, and team memberships.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | — | — | No parameters required |

**Example prompt:**

> "Who am I in PagerDuty? What teams am I on?"

---

### `list_users`

List users, optionally filtering by name and team IDs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `UserQuery` | No | Optional filtering parameters (name query, team IDs, pagination) |

**Example prompt:**

> "List all users on the platform team"
