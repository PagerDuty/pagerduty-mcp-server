---
sidebar_position: 15
---

# Status Pages

Status Pages let you communicate service health and incidents to your customers. These tools let you read status page configuration and create posts and updates.

## Tools

### `list_status_pages`

List Status Pages with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `StatusPageQuery` | No | Optional filtering parameters |

---

### `list_status_page_severities`

List severity levels for a Status Page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `query_model` | `StatusPageSeverityQuery` | No | Optional filtering parameters |

---

### `list_status_page_impacts`

List impact options for a Status Page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `query_model` | `StatusPageImpactQuery` | No | Optional filtering parameters |

---

### `list_status_page_statuses`

List status options for a Status Page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `query_model` | `StatusPageStatusQuery` | No | Optional filtering parameters |

---

### `get_status_page_post`

Get a specific status page post by post ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `post_id` | `string` | Yes | The ID of the Status Page Post |
| `query_model` | `StatusPagePostQuery` | No | Optional query parameters (e.g., include related resources) |

---

### `list_status_page_post_updates`

List updates for a specific status page post.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `post_id` | `string` | Yes | The ID of the Status Page Post |
| `query_model` | `StatusPagePostUpdateQuery` | No | Optional filtering parameters |

---

### `create_status_page_post` *(write)*

Create a new post (incident or maintenance) on a status page. All posts require `starts_at`, `ends_at`, and at least one update.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `create_model` | `StatusPagePostCreateRequestWrapper` | Yes | The post creation request |

The `create_model` must include:
- `post.title` — The title of the post
- `post.post_type` — Either `"incident"` or `"maintenance"`
- `post.starts_at` — When the post becomes effective (ISO datetime, required)
- `post.ends_at` — When the post is concluded (ISO datetime, required)
- `post.updates` — List of at least one post update with message, status, severity, etc.

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Create a status page incident post on status page PXXXXXX titled 'API Degradation' starting now"

---

### `create_status_page_post_update` *(write)*

Add a new update to an existing status page post.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_page_id` | `string` | Yes | The ID of the Status Page |
| `post_id` | `string` | Yes | The ID of the Status Page Post |
| `create_model` | `StatusPagePostUpdateRequestWrapper` | Yes | The post update creation request |

The `create_model` must include:
- `post_update.message` — The message text for the update (required)
- `post_update.status` — Status reference (required)
- `post_update.severity` — Severity reference (required)
- `post_update.post` — Post reference (required)

Optional fields:
- `post_update.impacted_services` — List of impacted services (defaults to empty list)
- `post_update.notify_subscribers` — Whether to notify subscribers (defaults to `false`)
- `post_update.update_frequency_ms` — Update frequency in milliseconds (defaults to `null`)

:::note
Requires `--enable-write-tools` flag.
:::
