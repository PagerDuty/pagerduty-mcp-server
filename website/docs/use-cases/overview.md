---
sidebar_position: 1
---

# Use Cases Overview

This section collects real-world use cases for the PagerDuty MCP Server — contributed by the FDE team and the community. Each use case includes a scenario description, the tools involved, and example prompts you can use directly in your AI client.

Use these as a starting point, adapt them to your environment, and share your own workflows back with the community.

## Available Use Cases

| Use Case | Tools Used | Mode |
|----------|-----------|------|
| [Incident Investigation](./incident-investigation) | `list_incidents`, `get_incident`, `list_incident_notes`, `list_alerts_from_incident`, `list_incident_change_events` | Read-only |
| [On-Call Handoff](./on-call-handoff) | `list_oncalls`, `list_schedules`, `list_incidents`, `get_user_data` | Read-only |
| [Service Health Check](./service-health-check) | `list_services`, `list_incidents`, `list_change_events`, `list_log_entries` | Read-only |
| [Incident Response Automation](./incident-response-automation) | `create_incident`, `manage_incidents`, `add_responders`, `add_note_to_incident`, `start_incident_workflow` | Write |

## How to contribute

Found a workflow that saves your team time? We'd love to add it here.

Open a pull request against [pagerduty-mcp-server-docs](https://github.com/PagerDuty/pagerduty-mcp-server-docs) with a new file under `docs/use-cases/` following the format of any existing use case page.
