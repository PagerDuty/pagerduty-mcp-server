---
sidebar_position: 2
---

# Alert Grouping

Alert grouping settings control how PagerDuty automatically groups alerts into incidents, reducing noise and helping responders focus on related issues.

## Tools

### `list_alert_grouping_settings`

List all alert grouping settings with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `AlertGroupingSettingQuery` | No | Optional filtering parameters |

---

### `get_alert_grouping_setting`

Get details for a specific alert grouping setting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `setting_id` | `string` | Yes | The ID of the alert grouping setting to retrieve |

---

### `create_alert_grouping_setting` *(write)*

Create a new alert grouping setting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `create_model` | `AlertGroupingSettingCreateRequest` | Yes | The alert grouping setting creation request |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `update_alert_grouping_setting` *(write)*

Update an existing alert grouping setting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `setting_id` | `string` | Yes | The ID of the alert grouping setting to update |
| `update_model` | `AlertGroupingSettingUpdateRequest` | Yes | The alert grouping setting update request |

:::note
Requires `--enable-write-tools` flag.
:::

---

### `delete_alert_grouping_setting` *(write)*

Delete an alert grouping setting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `setting_id` | `string` | Yes | The ID of the alert grouping setting to delete |

:::note
Requires `--enable-write-tools` flag.
:::
