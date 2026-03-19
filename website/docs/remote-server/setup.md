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
- Uses **OAuth 2.0** for authentication — no API tokens to manage locally
- Exposes tools via a remote HTTP/SSE endpoint
- Requires no local Python installation or `uvx`

## Setup Steps

### 1. Authorize via OAuth

Navigate to the PagerDuty MCP API page to initiate the OAuth flow. You will be redirected to authorize the MCP client with your PagerDuty account.

The OAuth flow grants the remote server permission to act on your behalf using your PagerDuty account credentials.

### 2. Get the Remote Endpoint URL

After authorization, you will receive a remote MCP endpoint URL in the format:

```
https://mcp.pagerduty.com/sse
```

### 3. Configure Your MCP Client

#### Cursor

Add to `~/.cursor/mcp.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pagerduty": {
      "url": "https://mcp.pagerduty.com/sse"
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
        "type": "sse",
        "url": "https://mcp.pagerduty.com/sse"
      }
    }
  }
}
```

## Comparison: Remote vs. Local Server

| Feature | Remote Server | Local Server |
|---------|--------------|-------------|
| Installation required | None | Python + uv or Docker |
| Authentication | OAuth 2.0 | API Token (`PAGERDUTY_USER_API_KEY`) |
| Write tools | Configured at OAuth level | `--enable-write-tools` flag |
| Tool filtering | Not supported | Via `mcp-proxy` |
| EU region support | Automatic | `PAGERDUTY_API_HOST` env var |
| Offline use | No | Yes |

## Limitations

- **Tool filtering** via [`mcp-proxy`](../configuration/tool-filtering) is not available for the remote server (the proxy approach requires a local subprocess to intercept)
- Write access depends on the OAuth app permissions granted during authorization
- The remote server does not support the `--enable-write-tools` flag

## Troubleshooting

If you cannot connect to the remote server:

1. Verify your OAuth authorization is still valid — re-authorize if the token has expired
2. Check that your MCP client supports remote/SSE-based MCP connections
3. Consult the [PagerDuty Developer Portal](https://developer.pagerduty.com/api-reference/d71edf8527b5e-pager-duty-mcp-api) for the latest endpoint URLs and requirements
