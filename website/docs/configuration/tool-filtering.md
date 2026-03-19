---
sidebar_position: 3
---

# Tool Filtering

The PagerDuty MCP Server exposes **55 tools** across 14 domains. While comprehensive, this large number of tools can degrade AI performance — LLMs perform better with a focused, relevant set of tools.

This guide explains how to filter tools using [`mcp-proxy`](https://github.com/TBXark/mcp-proxy), a lightweight proxy server that sits between your MCP client and the PagerDuty MCP Server.

:::info Background
This solution addresses the request in [GitHub Issue #68](https://github.com/PagerDuty/pagerduty-mcp-server/issues/68): *"Can we add a flag to filter MCP tools by area?"* While native filtering is not yet built into the server, the `mcp-proxy` approach provides an effective workaround.
:::

## How It Works

```
MCP Client → mcp-proxy (localhost:9090) → PagerDuty MCP Server
                   ↑
            Tool filter applied here
```

The proxy starts the PagerDuty MCP Server as a subprocess and only forwards a selected subset of tools to your client.

## Installation

Install `mcp-proxy`:

```bash
# Using Go
go install github.com/TBXark/mcp-proxy@latest

# Or download a pre-built binary from:
# https://github.com/TBXark/mcp-proxy/releases
```

## Configuration

Create a `mcp_proxy_config.json` file:

### Allow List (Whitelist)

Only expose the tools you explicitly list:

```json
{
  "mcpProxy": {
    "baseURL": "http://localhost:9090",
    "addr": ":9090",
    "type": "streamable-http"
  },
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      },
      "options": {
        "toolFilter": {
          "mode": "allow",
          "list": [
            "get_user_data",
            "list_incidents",
            "get_incident",
            "list_oncalls",
            "list_schedules"
          ]
        }
      }
    }
  }
}
```

### Deny List (Blacklist)

Expose all tools except those you list:

```json
{
  "mcpProxy": {
    "baseURL": "http://localhost:9090",
    "addr": ":9090",
    "type": "streamable-http"
  },
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      },
      "options": {
        "toolFilter": {
          "mode": "deny",
          "list": [
            "list_status_pages",
            "list_status_page_severities",
            "list_status_page_impacts",
            "list_status_page_statuses",
            "get_status_page_post",
            "list_status_page_post_updates",
            "create_status_page_post",
            "create_status_page_post_update"
          ]
        }
      }
    }
  }
}
```

### With Write Tools

```json
{
  "mcpProxy": {
    "baseURL": "http://localhost:9090",
    "addr": ":9090",
    "type": "streamable-http"
  },
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp", "--enable-write-tools"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      },
      "options": {
        "toolFilter": {
          "mode": "allow",
          "list": [
            "list_incidents",
            "get_incident",
            "create_incident",
            "manage_incidents",
            "add_note_to_incident"
          ]
        }
      }
    }
  }
}
```

## Starting the Proxy

```bash
mcp-proxy --config mcp_proxy_config.json
```

The proxy starts on `http://localhost:9090` by default.

## Configuring Your MCP Client

Point your client to the proxy instead of running the server directly.

### Cursor / Claude Desktop

```json
{
  "mcpServers": {
    "pagerduty": {
      "url": "http://localhost:9090/mcp"
    }
  }
}
```

### VS Code

```json
{
  "mcp": {
    "servers": {
      "pagerduty": {
        "type": "http",
        "url": "http://localhost:9090/mcp"
      }
    }
  }
}
```

## Suggested Tool Sets by Use Case

| Use Case | Recommended Tools |
|----------|-------------------|
| Incident Management | `list_incidents`, `get_incident`, `list_incident_notes`, `manage_incidents`, `add_note_to_incident` |
| On-Call Overview | `list_oncalls`, `list_schedules`, `get_schedule`, `list_schedule_users` |
| Service Health | `list_services`, `get_service`, `list_change_events`, `list_log_entries` |
| Team Operations | `list_teams`, `get_team`, `list_team_members`, `list_users` |
| Minimal Read-Only | `get_user_data`, `list_incidents`, `get_incident`, `list_oncalls`, `list_schedules` |
