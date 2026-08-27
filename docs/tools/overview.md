# Tools Overview

The PagerDuty MCP Server exposes **103 tools** across **19 domains**. By default, only the 63 read-only tools are available. The 40 write tools require starting the server with `--enable-write-tools`.

## Read vs. Write Tools

| Type | Count | Flag Required |
|------|-------|---------------|
| Read-only | 63 | None (always available) |
| Write | 40 | `--enable-write-tools` |
| **Total** | **103** | |

## Complete Tool Reference

### Alert Grouping

| Tool | Type | Description |
|------|------|-------------|
| `list_alert_grouping_settings` | Read | List all alert grouping settings |
| `get_alert_grouping_setting` | Read | Get a specific alert grouping setting |
| `create_alert_grouping_setting` | Write | Create a new alert grouping setting |
| `update_alert_grouping_setting` | Write | Update an alert grouping setting |
| `delete_alert_grouping_setting` | Write | Delete an alert grouping setting |

### Alerts

| Tool | Type | Description |
|------|------|-------------|
| `list_alerts_from_incident` | Read | List alerts associated with an incident |
| `get_alert_from_incident` | Read | Get a specific alert from an incident |

### Analytics

| Tool | Type | Description |
|------|------|-------------|
| `get_responder_metrics` | Read | Get per-responder on-call hours and interruption counts by team |
| `get_incident_metrics_by_service` | Read | Get aggregated MTTA, MTTR, and uptime metrics per service |
| `get_incident_metrics_by_team` | Read | Get aggregated incident metrics per team with optional time-series breakdown |
| `get_responder_load_metrics` | Read | Get per-responder load metrics across all teams |
| `get_incident_metrics_all` | Read | Get full-period aggregated metrics including P50-P95 percentiles |

### Business Services

| Tool | Type | Description |
|------|------|-------------|
| `list_business_services` | Read | List all business services |
| `get_business_service_dependencies` | Read | Get technical service dependencies for a business service |

### Change Events

| Tool | Type | Description |
|------|------|-------------|
| `list_change_events` | Read | List change events across all services |
| `get_change_event` | Read | Get a specific change event |
| `list_service_change_events` | Read | List change events for a specific service |
| `list_incident_change_events` | Read | List change events related to an incident |

### Incidents

| Tool | Type | Description |
|------|------|-------------|
| `list_incidents` | Read | List incidents with filters |
| `get_incident` | Read | Get a specific incident by ID |
| `get_outlier_incident` | Read | Get outlier incident analysis |
| `get_past_incidents` | Read | Get past incidents similar to a given one |
| `get_related_incidents` | Read | Get incidents related to a given one |
| `list_incident_notes` | Read | List notes on an incident |
| `create_incident` | Write | Create a new incident |
| `manage_incidents` | Write | Update incident status, priority, or assignees |
| `add_responders` | Write | Add responders to an incident |
| `add_note_to_incident` | Write | Add a note to an incident |

### Incident Workflows

| Tool | Type | Description |
|------|------|-------------|
| `list_incident_workflows` | Read | List incident workflows |
| `get_incident_workflow` | Read | Get a specific incident workflow |
| `start_incident_workflow` | Write | Trigger an incident workflow |

### Services

| Tool | Type | Description |
|------|------|-------------|
| `list_services` | Read | List all services |
| `get_service` | Read | Get a specific service |
| `get_technical_service_dependencies` | Read | Get dependencies for a technical service |
| `create_service` | Write | Create a new service |
| `update_service` | Write | Update a service configuration |

### Teams

| Tool | Type | Description |
|------|------|-------------|
| `list_teams` | Read | List all teams |
| `get_team` | Read | Get a specific team |
| `list_team_members` | Read | List members of a team |
| `create_team` | Write | Create a new team |
| `update_team` | Write | Update team details |
| `delete_team` | Write | Delete a team |
| `add_team_member` | Write | Add a user to a team |
| `remove_team_member` | Write | Remove a user from a team |

### Users

| Tool | Type | Description |
|------|------|-------------|
| `get_user_data` | Read | Get the current authenticated user's information |
| `list_users` | Read | List all users in the account |
| `create_user` | Write | Create a new PagerDuty user account. No invitation email is sent |

### Schedules

| Tool | Type | Description |
|------|------|-------------|
| `list_schedules` | Read | List all on-call schedules |
| `get_schedule` | Read | Get a specific schedule |
| `list_schedule_users` | Read | List users on a schedule for a time range |
| `create_schedule` | Write | Create a new on-call schedule |
| `update_schedule` | Write | Update an existing schedule |
| `create_schedule_override` | Write | Add an override to a schedule |

### Schedules (shift-based v3 sub-resources)

| Tool | Type | Description |
|------|------|-------------|
| `list_schedule_v3_rotations` | Read | List all rotations for a v3 schedule |
| `get_schedule_v3_rotation` | Read | Get a specific rotation within a v3 schedule |
| `list_schedule_v3_rotation_events` | Read | List all events for a rotation in a v3 schedule |
| `get_schedule_v3_rotation_event` | Read | Get a specific event within a v3 schedule rotation |
| `list_schedule_v3_custom_shifts` | Read | List custom shifts for a v3 schedule within a time range |
| `get_schedule_v3_custom_shift` | Read | Get a specific custom shift within a v3 schedule |
| `list_schedule_v3_overrides` | Read | List overrides for a v3 schedule within a time range |
| `get_schedule_v3_override` | Read | Get a specific override within a v3 schedule |
| `delete_schedule_v3` | Write | Delete a v3 schedule |
| `create_schedule_v3_rotation` | Write | Create a new rotation within a v3 schedule |
| `delete_schedule_v3_rotation` | Write | Delete a rotation from a v3 schedule |
| `create_schedule_v3_rotation_event` | Write | Create a new event within a v3 schedule rotation |
| `update_schedule_v3_rotation_event` | Write | Update an existing rotation event in a v3 schedule |
| `delete_schedule_v3_rotation_event` | Write | Delete an event from a v3 schedule rotation |
| `create_schedule_v3_custom_shifts` | Write | Create one or more custom shifts for a v3 schedule |
| `update_schedule_v3_custom_shift` | Write | Update an existing custom shift in a v3 schedule |
| `delete_schedule_v3_custom_shift` | Write | Delete a custom shift from a v3 schedule |
| `create_schedule_v3_overrides` | Write | Create one or more overrides for a v3 schedule |
| `update_schedule_v3_override` | Write | Update an existing override in a v3 schedule |
| `delete_schedule_v3_override` | Write | Delete an override from a v3 schedule |

### On-Call

| Tool | Type | Description |
|------|------|-------------|
| `list_oncalls` | Read | List current on-call assignments |

### Priorities

| Tool | Type | Description |
|------|------|-------------|
| `list_priorities` | Read | List all incident priority levels configured in the account |

### Log Entries

| Tool | Type | Description |
|------|------|-------------|
| `list_log_entries` | Read | List log entries (audit trail) |
| `get_log_entry` | Read | Get a specific log entry |

### Escalation Policies

| Tool | Type | Description |
|------|------|-------------|
| `list_escalation_policies` | Read | List all escalation policies |
| `get_escalation_policy` | Read | Get a specific escalation policy |
| `create_escalation_policy` | Write | Create a new escalation policy |
| `update_escalation_policy` | Write | Update an existing escalation policy |

### Event Orchestrations

| Tool | Type | Description |
|------|------|-------------|
| `list_event_orchestrations` | Read | List event orchestrations |
| `get_event_orchestration` | Read | Get a specific event orchestration |
| `get_event_orchestration_router` | Read | Get orchestration router configuration |
| `get_event_orchestration_service` | Read | Get service-level orchestration rules |
| `get_event_orchestration_global` | Read | Get global orchestration rules |
| `update_event_orchestration_router` | Write | Update the orchestration router |
| `append_event_orchestration_router_rule` | Write | Add a rule to the orchestration router |

### Status Pages

| Tool | Type | Description |
|------|------|-------------|
| `list_status_pages` | Read | List all status pages |
| `list_status_page_severities` | Read | List severity levels for a status page |
| `list_status_page_impacts` | Read | List impact options for a status page |
| `list_status_page_statuses` | Read | List status options for a status page |
| `get_status_page_post` | Read | Get a specific status page post |
| `list_status_page_post_updates` | Read | List updates for a status page post |
| `create_status_page_post` | Write | Create a new status page post |
| `create_status_page_post_update` | Write | Add an update to a status page post |

### Webhooks & Extension Schemas

| Tool | Type | Description |
|------|------|-------------|
| `list_webhook_subscriptions` | Read | List webhook subscriptions |
| `get_webhook_subscription` | Read | Get a specific webhook subscription by ID |
| `list_extension_schemas` | Read | List available extension schemas (extension vendors) |
| `get_extension_schema` | Read | Get a specific extension schema by ID |
| `create_webhook_subscription` | Write | Create a new webhook subscription |
| `update_webhook_subscription` | Write | Update an existing webhook subscription |
| `delete_webhook_subscription` | Write | Delete a webhook subscription |

## Detailed Reference

See the individual domain pages for parameter details and usage examples:

- [Alert Grouping](./alert-grouping.md) · [Alerts](./alerts.md) · [Analytics](./analytics.md)
- [Business Services](./business-services.md) · [Change Events](./change-events.md)
- [Incidents](./incidents.md) · [Incident Workflows](./incident-workflows.md)
- [Services](./services.md) · [Teams](./teams.md) · [Users](./users.md)
- [Schedules](./schedules.md) · [On-Call](./oncalls.md) · [Priorities](./priorities.md)
- [Log Entries](./log-entries.md) · [Escalation Policies](./escalation-policies.md)
- [Event Orchestrations](./event-orchestrations.md) · [Status Pages](./status-pages.md)
