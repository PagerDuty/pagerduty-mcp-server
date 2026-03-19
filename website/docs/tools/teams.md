---
sidebar_position: 8
---

# Teams

Teams group users and services together for organizational purposes. They are used to assign ownership of services and filter incidents by team.

## Tools

### `list_teams`

List teams based on optional query parameters.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `TeamQuery` | No | Query parameters (name filter, pagination, etc.) |

**Example prompt:**

> "List all teams in my PagerDuty account"

---

### `get_team`

Get a specific team by ID or name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID or name of the team to retrieve |

---

### `list_team_members`

List members of a team.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the team |

**Example prompt:**

> "Who are the members of the platform team?"

---

### `create_team` *(write)*

Create a new team.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `create_model` | `TeamCreateRequest` | Yes | The team creation data (name, description) |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `update_team` *(write)*

Update an existing team.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the team to update |
| `update_model` | `TeamCreateRequest` | Yes | The updated team data |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `delete_team` *(write)*

Delete a team.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the team to delete |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `add_team_member` *(write)*

Add a user to a team.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the team to add the user to |
| `member_data` | `TeamMemberAdd` | Yes | Object containing the user ID and role to add to the team |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Add user PXXXXXX to the platform team as a responder"

---

### `remove_team_member` *(write)*

Remove a user from a team.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the team to remove the user from |
| `user_id` | `string` | Yes | The ID of the user to remove |

:::note
Requires `--enable-write-tools` flag.
:::
