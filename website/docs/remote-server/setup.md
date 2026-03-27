---
sidebar_position: 1
---

# Remote MCP Server Setup

The **PagerDuty Remote MCP Server** is a PagerDuty-hosted service that lets you connect your AI assistant to PagerDuty without installing anything locally. It uses OAuth for authentication, making it easy to set up across teams and enterprise environments.

:::info Official Reference
For the most up-to-date setup instructions, refer to the [PagerDuty MCP API documentation](https://developer.pagerduty.com/api-reference/d71edf8527b5e-pager-duty-mcp-api) on the PagerDuty Developer Portal.
:::

## Prerequisites

- A PagerDuty account with API access
- An MCP-compatible client that supports remote/HTTP-based MCP servers (Cursor, VS Code, etc.)

## How It Works

Unlike the local server that runs as a subprocess on your machine, the remote server:

- Is hosted and maintained by PagerDuty
- Exposes tools via a remote HTTP endpoint
- Requires no local Python installation or `uvx`

## Setup Steps

### Configure Your MCP Client

#### Cursor

Add to `~/.cursor/mcp.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pagerduty": {
      "url": "https://mcp.pagerduty.com/mcp"
    }
  }
}
```

#### VS Code

Add to `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "pagerduty": {
        "type": "http",
        "url": "https://mcp.pagerduty.com/mcp"
      }
    }
  }
}
```

## Comparison: Remote vs. Local Server

| Feature | Remote Server | Local Server |
|---------|--------------|-------------|
| Installation required | None | Python + uv or Docker |
| Tool filtering | Not supported | Via `mcp-proxy` |
| EU region support | Automatic | `PAGERDUTY_API_HOST` env var |
| Offline use | No | Yes |

## Limitations

- **Tool filtering** via [`mcp-proxy`](../configuration/tool-filtering) is not available for the remote server (the proxy approach requires a local subprocess to intercept)

## Troubleshooting

If you cannot connect to the remote server:

1. Verify your PagerDuty User Token is still valid — re-generate a new one. [More details here](https://developer.pagerduty.com/docs/authentication).
2. Check that your MCP client supports remote/HTTP-based MCP connections
3. Consult the [PagerDuty Developer Portal](https://developer.pagerduty.com/api-reference/d71edf8527b5e-pager-duty-mcp-api) for the latest endpoint URLs and requirements
