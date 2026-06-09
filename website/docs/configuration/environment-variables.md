---
sidebar_position: 1
---

# Environment Variables

The PagerDuty MCP Server uses the following environment variables.

## Required

| Variable | Description |
|----------|-------------|
| `PAGERDUTY_USER_API_KEY` | Your PagerDuty User API Token. See [Authentication](../getting-started/authentication). |

## Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `PAGERDUTY_API_HOST` | `https://api.pagerduty.com` | PagerDuty API endpoint. Set to `https://api.eu.pagerduty.com` for EU accounts. |

## Setting Variables

### Shell

```bash
export PAGERDUTY_USER_API_KEY="your-token"
export PAGERDUTY_API_HOST="https://api.eu.pagerduty.com"  # EU only
```

### MCP Client Config

Most clients accept an `env` block in their MCP server configuration:

```json
{
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-token",
        "PAGERDUTY_API_HOST": "https://api.eu.pagerduty.com"
      }
    }
  }
}
```

### Docker

Pass variables with `-e` flags:

```bash
docker run --rm -i \
  -e PAGERDUTY_USER_API_KEY="your-token" \
  -e PAGERDUTY_API_HOST="https://api.eu.pagerduty.com" \
  ghcr.io/pagerduty/pagerduty-mcp:latest
```
