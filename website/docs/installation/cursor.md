---
sidebar_position: 1
---

# Cursor

[Cursor](https://cursor.sh) supports MCP servers natively. This guide shows how to add the PagerDuty MCP Server to Cursor.

## Global Configuration

Create or edit `~/.cursor/mcp.json`:

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

## Project-Level Configuration

To use different credentials per project, create `.cursor/mcp.json` in your project root with the same structure.

## With Write Tools Enabled

To enable state-modifying tools (create incident, manage team, etc.):

```json
{
  "mcpServers": {
    "pagerduty": {
      "command": "uvx",
      "args": ["pagerduty-mcp", "--enable-write-tools"],
      "env": {
        "PAGERDUTY_USER_API_KEY": "your-api-token-here"
      }
    }
  }
}
```

## Verify

After saving the config, restart Cursor. In the chat panel (Agent mode), the PagerDuty tools should be listed under available MCP tools.

:::tip
Use [Tool Filtering](../configuration/tool-filtering) to limit tools to a specific subset for better AI performance.
:::
