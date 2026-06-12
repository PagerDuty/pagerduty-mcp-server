# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0]

### Changed — ⚠️ Breaking Change

**Flatten tool function signatures: `query_model` replaced with individual parameters**

The following list tools previously accepted a single `query_model` parameter wrapping a Pydantic
query object. They now accept individual typed parameters directly. This eliminates `$ref` / `$defs`
entries from the tool input schemas, making all tools usable by non-Claude MCP clients (GitHub
Copilot CLI, Cursor, AWS Bedrock).

#### Affected tools and migration

| Tool | Old signature | New signature |
|---|---|---|
| `list_alert_grouping_settings` | `query_model: AlertGroupingSettingQuery \| None` | `service_ids`, `limit`, `after`, `before`, `total` |
| `list_alerts_from_incident` | `incident_id`, `query_model: AlertQuery` | `incident_id`, `limit`, `offset` |
| `list_change_events` | `query_model: ChangeEventQuery \| None` | `since`, `until`, `limit`, `offset`, `total`, `team_ids`, `integration_ids` |
| `list_service_change_events` | `service_id`, `query_model: ChangeEventQuery \| None` | `service_id`, `since`, `until`, `limit`, `offset`, `total`, `team_ids`, `integration_ids` |
| `list_event_orchestrations` | `query_model: EventOrchestrationQuery \| None` | `limit`, `offset`, `sort_by` |
| `list_incident_workflows` | `query_model: IncidentWorkflowQuery \| None` | `limit`, `query`, `include` |
| `list_oncalls` | `query_model: OncallQuery \| None` | `time_zone`, `user_ids`, `escalation_policy_ids`, `schedule_ids`, `service_ids`, `since`, `until`, `earliest`, `limit` |
| `list_teams` | `query_model: TeamQuery \| None` | `scope`, `query`, `limit` |

If you are calling these tools programmatically using the old nested `{"query_model": {...}}`
shape, update your calls to pass each field as a top-level argument instead. For example:

```json
// Before
{"query_model": {"query": "production", "limit": 25}}

// After
{"query": "production", "limit": 25}
```
