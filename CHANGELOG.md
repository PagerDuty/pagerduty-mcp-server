# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed — ⚠️ Breaking Change

**FDE-230 / FDE-319: Tool input schemas no longer use `$ref` / `$defs`**

All list tools that previously accepted a single `query_model` parameter wrapping a Pydantic
query object now accept individual scalar parameters instead. This removes all `$ref` / `$defs`
entries from MCP tool schemas, restoring compatibility with non-Claude MCP clients (GitHub
Copilot CLI, Cursor, AWS Bedrock), and reduces the total startup schema footprint by ~80%.

#### Affected tools and migration

| Tool | Old signature | New signature |
|---|---|---|
| `list_services` | `query_model: ServiceQuery \| None` | `query`, `teams_ids`, `limit` |
| `list_escalation_policies` | `query_model: EscalationPolicyQuery \| None` | `query`, `user_ids`, `team_ids`, `include`, `limit` |
| `list_schedules` | `query_model: ScheduleQuery \| None` | `query`, `team_ids`, `user_ids`, `include`, `limit` |
| `list_oncalls` | `query_model: OncallQuery \| None` | `time_zone`, `user_ids`, `escalation_policy_ids`, `schedule_ids`, `since`, `until`, `earliest`, `limit` |
| `list_teams` | `query_model: TeamQuery \| None` | `scope`, `query`, `limit` |
| `list_incidents` | `query_model: IncidentQuery` | `statuses`, `since`, `until`, `user_ids`, `service_ids`, `teams_ids`, `urgencies`, `sort_by`, `request_scope`, `limit` |

If you are calling these tools programmatically using the old nested `{"query_model": {...}}`
shape, update your calls to pass each field as a top-level argument instead. For example:

```json
// Before
{"query_model": {"query": "production", "limit": 25}}

// After
{"query": "production", "limit": 25}
```
