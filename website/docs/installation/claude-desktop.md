---
sidebar_position: 3
---

# Claude Desktop

[Claude Desktop](https://claude.ai/download) supports local MCP servers. This guide shows how to add the PagerDuty MCP Server.

## Configuration File Location

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

## Configuration

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

## With Write Tools

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

Restart Claude Desktop. A hammer icon in the chat input area indicates MCP tools are loaded. Click it to confirm PagerDuty tools are listed.

:::caution
The API token is stored in the config file in plaintext. Ensure the file has appropriate permissions:
```bash
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```
:::
