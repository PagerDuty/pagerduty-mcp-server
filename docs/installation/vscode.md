# VS Code

VS Code supports MCP servers in [Agent mode](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) (GitHub Copilot Chat). This guide shows how to configure the PagerDuty MCP Server.

## Enable MCP

Before configuring the server, search for `mcp` in VS Code settings and make sure
**Mcp: Enabled** is checked under **Features → Chat**.

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

1. Open the Chat panel in VS Code (**View → Chat**) and switch to **Agent** mode.
2. Click the 🛠️ icon to see the PagerDuty tools listed — you can enable or disable individual tools
   here. For a durable way to reduce the tool count, see
   [Tool Filtering](../configuration/tool-filtering.md).
3. Try a prompt such as `Show me the latest incident` or `List my event orchestrations`.

## Troubleshooting

Manage the server from the command palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) → `MCP: List Servers`.
From there you can start, stop, and restart the server. Confirm it is running before sending prompts —
restarting it resolves most connection issues.
