# Service Health Matrix - Diagnostic Checklist

## Issue
Tools from pagerduty-mcp server are not accessible when called from service-health-matrix MCP App UI.

## Verified Working
✅ service-health-matrix server running on http://localhost:3003/mcp
✅ pagerduty-mcp server works via stdio (299KB of tool definitions returned)
✅ mcp.json configuration is correct

## Communication Chain
```
service-health-matrix UI
    ↓ app.callServerTool()
VS Code Copilot (Host)
    ↓ forwards to
pagerduty-mcp server (Parent Server)
    ↓ returns response
VS Code Copilot (Host)
    ↓ returns to
service-health-matrix UI
```

## Troubleshooting Steps

### 1. Verify VS Code Copilot sees both servers
- Open Command Palette (Cmd+Shift+P)
- Search for "MCP" or "Model Context Protocol"
- Check if both `pagerduty-mcp` and `service-health-matrix` servers are listed
- Look for any initialization errors

### 2. Check VS Code Output Panel
- View → Output (Cmd+Shift+U)
- Select "MCP" or "GitHub Copilot" from dropdown
- Look for:
  - Initialization errors for pagerduty-mcp
  - API key prompt issues
  - Connection errors
  - Tool registration messages

### 3. Verify API Key Prompt
- VS Code should prompt for PagerDuty API key on first load
- Check if the prompt was answered
- If not prompted, try:
  - Completely quit VS Code (not just reload)
  - Start VS Code fresh
  - Wait for the API key prompt

### 4. Test pagerduty-mcp server directly in VS Code
Before testing the service-health-matrix app, try using pagerduty-mcp tools directly:
- Ask Copilot: "List PagerDuty services"
- Or: "Show me PagerDuty incidents"
- This tests if VS Code can communicate with pagerduty-mcp server at all

### 5. Check for multiple VS Code instances
- Make sure only one VS Code instance is running
- Multiple instances might compete for the stdio connection

## Expected Behavior
When working correctly:
1. User opens service-health-matrix in VS Code Copilot
2. UI loads and calls `app.callServerTool({ name: "list_services", ... })`
3. VS Code forwards the request to pagerduty-mcp server
4. pagerduty-mcp returns service data
5. VS Code forwards response to service-health-matrix UI
6. UI displays the health matrix

## Current Behavior
- service-health-matrix UI gets stuck loading
- No data returned from pagerduty-mcp tools
- Other pagerduty-mcp tools (list_incidents, list_teams) also don't work in Copilot

## Next Steps
1. **Check VS Code Output logs** - This is the most important step
2. **Test pagerduty-mcp tools directly in Copilot** - Verify server is initialized
3. **Completely restart VS Code** - Quit and reopen, not just reload window
4. **Share any error messages** - From Output panel or console

## Configuration Files
- MCP Config: `~/Library/Application Support/Code - Insiders/User/mcp.json`
- service-health-matrix: http://localhost:3003/mcp (streamableHttp)
- pagerduty-mcp: stdio via uv run

## Test Commands
```bash
# Test pagerduty-mcp server directly
PAGERDUTY_USER_API_KEY="your-key" \
  /opt/homebrew/bin/uv run \
  --directory /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server \
  python -m pagerduty_mcp --enable-write-tools

# Test service-health-matrix server
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/service-health-matrix
npm start
```
