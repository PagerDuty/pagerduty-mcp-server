# VS Code Global MCP Configuration

Configure the PagerDuty Visualization Server globally in VS Code so it's available in all workspaces.

## Global Settings Location

**macOS**: `~/Library/Application Support/Code/User/settings.json`
**Windows**: `%APPDATA%\Code\User\settings.json`
**Linux**: `~/.config/Code/User/settings.json`

## Configuration

Open your global VS Code settings:
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: "Preferences: Open User Settings (JSON)"
3. Add or merge this configuration:

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "pagerduty-api-key",
        "description": "PagerDuty API Key",
        "password": true
      }
    ],
    "servers": {
      "pagerduty-viz": {
        "type": "stdio",
        "command": "node",
        "args": [
          "/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/dist/index.js",
          "--stdio"
        ],
        "env": {
          "PAGERDUTY_API_KEY": "${input:pagerduty-api-key}",
          "PAGERDUTY_USER_EMAIL": "svillanelo@pagerduty.com"
        }
      }
    }
  }
}
```

## After Configuration

1. **Restart VS Code** or reload window (`Cmd+Shift+P` > "Developer: Reload Window")
2. **Open Chat panel**: `View` > `Chat` or `Cmd+I` (Mac) / `Ctrl+I` (Windows/Linux)
3. **Enable MCP tools**: Click the 🛠️ icon in Chat to see available tools
4. **Test the dashboard**:
   ```
   Show me incident trends
   ```

## Troubleshooting

### Server not appearing

- Verify the path is correct: `ls -la /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/dist/index.js`
- Check VS Code MCP logs: `Cmd+Shift+P` > "MCP: List Servers"
- Ensure MCP is enabled: Settings > Features > Chat > "Mcp: Enabled"

### API Key prompt not appearing

- VS Code will prompt for `pagerduty-api-key` on first use
- You can also set it directly in `env` instead of using `${input:pagerduty-api-key}`

### Dashboard not loading

- Check the Chat panel for error messages
- Open DevTools on the iframe: Right-click inside dashboard > Inspect
- Look for console errors in the iframe
