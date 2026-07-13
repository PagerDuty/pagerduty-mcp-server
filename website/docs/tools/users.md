---
sidebar_position: 9
---

# Users

User tools let you retrieve information about the currently authenticated user, list users in the account, and create new users.

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

---

### `create_user` *(write)*

Create a new PagerDuty user account. No invitation email is sent automatically.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | `CreateUserRequest` | Yes | User creation parameters including `name`, `email`, `role` (default: `"user"`), and `time_zone` (default: `"UTC"`) |

**Valid roles:** `admin`, `limited_user`, `observer`, `owner`, `read_only_user`, `restricted_access`, `read_only_limited_user`, `user`

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create a new user account for Jane Smith with email jane.smith@example.com in the America/New_York timezone"
