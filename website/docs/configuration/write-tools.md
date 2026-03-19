---
sidebar_position: 2
---

# Write Tools

By default, the PagerDuty MCP Server runs in **read-only mode** — only tools that read data from PagerDuty are available. This is the safest default for exploration and monitoring.

To enable tools that create or modify PagerDuty resources, start the server with the `--enable-write-tools` flag.

## Enabling Write Tools

### uvx

```bash
uvx pagerduty-mcp --enable-write-tools
```

### MCP Client Config

```json
{
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp", "--enable-write-tools"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-token"
      }
    }
  }
}
```

### Docker

```bash
docker run --rm -i \
  -e PAGERDUTY_USER_API_KEY="your-token" \
  ghcr.io/pagerduty/pagerduty-mcp:latest \
  --enable-write-tools
```

## Write Tools by Domain

| Domain | Write Tools |
|--------|------------|
| Alert Grouping | `create_alert_grouping_setting`, `update_alert_grouping_setting`, `delete_alert_grouping_setting` |
| Incidents | `create_incident`, `manage_incidents`, `add_responders`, `add_note_to_incident` |
| Incident Workflows | `start_incident_workflow` |
| Services | `create_service`, `update_service` |
| Teams | `create_team`, `update_team`, `delete_team`, `add_team_member`, `remove_team_member` |
| Schedules | `create_schedule`, `create_schedule_override`, `update_schedule` |
| Event Orchestrations | `update_event_orchestration_router`, `append_event_orchestration_router_rule` |
| Status Pages | `create_status_page_post`, `create_status_page_post_update` |

## Security Considerations

- Only enable write tools when necessary
- Ensure your AI client is configured to confirm before taking destructive actions
- Consider using [tool filtering](./tool-filtering) to expose only the write tools you need
