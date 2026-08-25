# Quick Start

Get the PagerDuty MCP Server running in your AI client in under 5 minutes.

## Step 1: Get Your API Token

Generate a PagerDuty User API Token — see [Authentication](./authentication.md) for instructions.

## Step 2: Add to Your MCP Client

Choose your client:

### Cursor

Add to `.cursor/mcp.json` in your project or `~/.cursor/mcp.json` globally:

```json
{
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

## Step 3: Verify

Restart your MCP client. You should see the PagerDuty tools available. Test with a simple query:

> "List my open PagerDuty incidents"

## Next Steps

- [Enable write tools](../configuration/write-tools.md) to manage incidents, teams, and more
- [Filter tools](../configuration/tool-filtering.md) to reduce the tool set for better AI performance
- [Full installation guides](../installation/cursor.md) for detailed per-client setup
