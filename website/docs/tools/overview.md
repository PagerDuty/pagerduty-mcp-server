---
sidebar_position: 1
---

# Tools Overview

The PagerDuty MCP Server exposes **55 tools** across **14 domains**. By default, only the 37 read-only tools are available. The 18 write tools require starting the server with `--enable-write-tools`.

## Read vs. Write Tools

| Type | Count | Flag Required |
|------|-------|---------------|
| Read-only | 37 | None (always available) |
| Write | 18 | `--enable-write-tools` |
| **Total** | **55** | |

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

### Schedules

| Tool | Type | Description |
|------|------|-------------|
| `list_schedules` | Read | List all on-call schedules |
| `get_schedule` | Read | Get a specific schedule |
| `list_schedule_users` | Read | List users on a schedule for a time range |
| `create_schedule` | Write | Create a new on-call schedule |
| `create_schedule_override` | Write | Add an override to a schedule |
| `update_schedule` | Write | Update an existing schedule |

### On-Call

| Tool | Type | Description |
|------|------|-------------|
| `list_oncalls` | Read | List current on-call assignments |

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

## Detailed Reference

See the individual domain pages for parameter details and usage examples:

- [Alert Grouping](./alert-grouping) · [Alerts](./alerts) · [Change Events](./change-events)
- [Incidents](./incidents) · [Incident Workflows](./incident-workflows)
- [Services](./services) · [Teams](./teams) · [Users](./users)
- [Schedules](./schedules) · [On-Call](./oncalls) · [Log Entries](./log-entries)
- [Escalation Policies](./escalation-policies) · [Event Orchestrations](./event-orchestrations) · [Status Pages](./status-pages)
