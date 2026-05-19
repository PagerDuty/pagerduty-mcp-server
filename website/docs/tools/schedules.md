---
sidebar_position: 10
---

# Schedules

On-call schedules define who is on-call at any given time. These tools let you view, create, and manage schedules and overrides.

## Tools

### `list_schedules`

List schedules with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `ScheduleQuery` | No | Optional filtering parameters (name, pagination) |

**Example prompt:**

> "List all on-call schedules"

---

### `get_schedule`

Get a specific schedule by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schedule_id` | `string` | Yes | The ID of the schedule to retrieve |

**Example prompt:**

> "Get the details for schedule PXXXXXX"

---

### `list_schedule_users`

List users in a schedule.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schedule_id` | `string` | Yes | The ID of the schedule |

**Example prompt:**

> "Who is on the primary on-call schedule?"

---

### `create_schedule` *(write)*

Create a new on-call schedule. Each schedule layer requires a `name` field to identify the layer.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `create_model` | `ScheduleCreateRequest` | Yes | The schedule creation data |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `create_schedule_override` *(write)*

Create an override for a schedule. The `override_request` contains an `overrides` array. Each override requires:
- `start` — ISO datetime when the override begins
- `end` — ISO datetime when the override ends
- `user_id` — The PagerDuty ID of the user covering the override

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schedule_id` | `string` | Yes | The ID of the schedule to override |
| `override_request` | `ScheduleOverrideCreate` | Yes | Data for the schedule override |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create an override for schedule PXXXXXX putting user PYYYYYY on-call from 2025-01-15T09:00:00Z to 2025-01-15T17:00:00Z"

---

### `update_schedule` *(write)*

Update an existing schedule.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schedule_id` | `string` | Yes | The ID of the schedule to update |
| `update_model` | `ScheduleUpdateRequest` | Yes | The updated schedule data |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `list_schedule_overrides`

List overrides for a schedule within a date range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schedule_id` | `string` | Yes | The ID of the schedule |
| `since` | `string` | Yes | Start of the date range (ISO 8601) |
| `until` | `string` | Yes | End of the date range (ISO 8601) |

**Example prompt:**

> "List all overrides for schedule PXXXXXX in January 2026"

---

### `delete_schedule_override` *(write)*

Delete a schedule override.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schedule_id` | `string` | Yes | The ID of the schedule |
| `override_id` | `string` | Yes | The ID of the override to delete |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Delete override OXXXXXX from schedule PXXXXXX"
