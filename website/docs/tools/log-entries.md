---
sidebar_position: 12
---

# Log Entries

Log entries are records of all events on your PagerDuty account — they form the complete audit trail of incident activity, notifications, and state changes. If no time range is specified, defaults to the last 7 days.

## Tools

### `list_log_entries`

List all log entries across the account with optional time range filtering and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `LogEntryQuery` | No | Query parameters including `since`, `until`, `limit`, and `offset`. Defaults to the last 7 days if no time range is specified. |

**Example prompts:**

> "Show me all log entries from the last hour"

> "List log entries between 2025-01-14T00:00:00Z and 2025-01-14T12:00:00Z"

---

### `get_log_entry`

Get a specific log entry by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `log_entry_id` | `string` | Yes | The ID of the log entry |

**Example prompt:**

> "Get log entry PXXXXXX"
