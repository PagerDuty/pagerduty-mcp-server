---
sidebar_position: 2
---

# VS Code

VS Code supports MCP servers in [Agent mode](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) (GitHub Copilot Chat). This guide shows how to configure the PagerDuty MCP Server.

## Configuration

Add to your VS Code `settings.json` (`Cmd+Shift+P` → `Open User Settings (JSON)`):

```json
{
  "mcp": {
    "servers": {
      "pagerduty": {
        "type": "stdio",
        "command": "uvx",
        "args": ["pagerduty-mcp"],
        "env": {
          "PAGERDUTY_USER_API_KEY": "${input:pagerdutapitoken}"
        }
      }
    },
    "inputs": [
      {
        "id": "pagerdutapitoken",
        "type": "promptString",
        "description": "PagerDuty User API Token",
        "password": true
      }
    ]
  }
}
```

The `${input:pagerdutapitoken}` syntax prompts you for the token securely — it is never stored in plaintext.

## With Write Tools

```json
{
  "mcp": {
    "servers": {
      "pagerduty": {
        "type": "stdio",
        "command": "uvx",
        "args": ["pagerduty-mcp", "--enable-write-tools"],
        "env": {
          "PAGERDUTY_USER_API_KEY": "${input:pagerdutapitoken}"
        }
      }
    }
  }
}
```

## Verify

Open the Chat panel in VS Code → switch to Agent mode → you should see PagerDuty tools listed.
