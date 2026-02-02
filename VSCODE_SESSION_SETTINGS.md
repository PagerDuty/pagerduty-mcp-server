# VS Code Session Settings Reference

This document details the VS Code settings used for the PagerDuty MCP Server development session.

## Workspace Settings

### Location
```
/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/.vscode/settings.json
```

### Complete Configuration

```json
{
  "claude.mcpServers": {
    "pagerduty-viz": {
      "command": "/Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node",
      "args": [
        "/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/dist/index.js",
        "--stdio"
      ],
      "env": {
        "PAGERDUTY_API_KEY": "${env:PAGERDUTY_API_KEY}",
        "PAGERDUTY_USER_EMAIL": "svillanelo@pagerduty.com"
      }
    }
  }
}
```

## Settings Breakdown

### MCP Server Configuration

| Property | Value | Description |
|----------|-------|-------------|
| **Server Name** | `pagerduty-viz` | Unique identifier for this MCP server instance |
| **Property Name** | `claude.mcpServers` | VS Code property for Claude integration (workspace-scoped) |

### Command Configuration

| Property | Value | Purpose |
|----------|-------|---------|
| **command** | `/Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node` | Full absolute path to Node.js v22.22.0 binary installed via nvm |
| **args[0]** | `/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/dist/index.js` | Full absolute path to built MCP server entry point |
| **args[1]** | `--stdio` | Transport protocol (stdio = standard input/output) |

### Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| **PAGERDUTY_API_KEY** | `${env:PAGERDUTY_API_KEY}` | Reads from shell environment variable (secure) |
| **PAGERDUTY_USER_EMAIL** | `svillanelo@pagerduty.com` | PagerDuty account email (hardcoded) |

## Why These Settings?

### Node.js Path

**Full path required**: `/Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node`

- ✅ Ensures exact Node.js version (v22.22.0)
- ✅ Avoids PATH resolution issues in VS Code
- ✅ Required for `import.meta.filename` support (Node 20.11+)

**How to find your path**:
```bash
which node
# Output: /Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node
```

### Index.js Path

**Full path required**: `/path/to/mcp-apps/dist/index.js`

- ✅ VS Code MCP servers must use absolute paths
- ✅ Relative paths don't work (VS Code working directory varies)
- ✅ Points to built server with shebang (`#!/usr/bin/env node`)

### Stdio Transport

**Why `--stdio`**:
- Standard MCP transport mechanism
- Uses stdin/stdout for JSON-RPC communication
- Compatible with all MCP clients (VS Code, Claude Desktop, etc.)

### Environment Variables

**Why `${env:PAGERDUTY_API_KEY}`**:

- ✅ **Security**: API key not hardcoded in config file
- ✅ **Flexibility**: Can be set per shell session/terminal
- ✅ **Git safety**: Settings file can be committed without exposing secrets

**Setting the environment variable**:
```bash
# In shell profile (~/.zshrc, ~/.bashrc)
export PAGERDUTY_API_KEY="your-api-key-here"

# Or per-session
export PAGERDUTY_API_KEY="your-key"
code /path/to/workspace
```

⚠️ **Important**: VS Code must be launched from a terminal with the environment variable set, or restart VS Code after setting it globally in your shell profile.

## Alternative Configuration: User Settings

For global availability across all workspaces:

### Location
```
macOS: ~/Library/Application Support/Code/User/settings.json
Windows: %APPDATA%\Code\User\settings.json
Linux: ~/.config/Code/User/settings.json
```

### Configuration with Secure Input Prompts

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
        "command": "/Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node",
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

### Differences from Workspace Settings

| Aspect | Workspace (`claude.mcpServers`) | User (`mcp.servers`) |
|--------|--------------------------------|---------------------|
| **Scope** | Current workspace only | All workspaces |
| **Property** | `claude.mcpServers` | `mcp.servers` |
| **API Key** | `${env:VAR}` from shell | `${input:ID}` prompts user |
| **Security** | Requires env var setup | Prompts once, stores in keychain |
| **Type field** | Not required | Required: `"type": "stdio"` |

## Environment Setup

### Shell Environment Variables

These environment variables should be set in your shell profile:

**macOS/Linux** (`~/.zshrc` or `~/.bashrc`):
```bash
# PagerDuty MCP Server
export PAGERDUTY_API_KEY="your-api-key-here"
export PAGERDUTY_USER_EMAIL="svillanelo@pagerduty.com"
export PAGERDUTY_API_HOST="https://api.pagerduty.com"  # Optional

# Bun (required for builds)
export PATH="$HOME/.bun/bin:$PATH"

# Node.js (if using nvm)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

**Apply changes**:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### VS Code Terminal Settings

Ensure VS Code uses your shell profile:

**Settings → Terminal**:
```json
{
  "terminal.integrated.inheritEnv": true,
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.profiles.osx": {
    "zsh": {
      "path": "/bin/zsh",
      "args": ["-l"]  // Login shell (loads profile)
    }
  }
}
```

## Verification Checklist

After configuring, verify everything works:

### 1. Check Environment
```bash
# In VS Code integrated terminal
echo $PAGERDUTY_API_KEY    # Should show your API key
echo $PAGERDUTY_USER_EMAIL # Should show your email
node --version             # Should be v20.11+ or v22+
```

### 2. Verify Build Output
```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps
ls -lh dist/

# Expected:
# -rw-r--r--  mcp-app.html   (~759KB)
# -rwxr-xr-x  index.js       (~45KB)
# -rw-r--r--  server.js      (~120KB)
```

### 3. Test MCP Server
```bash
# Run server directly (should output MCP protocol messages)
/Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node \
  /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/dist/index.js \
  --stdio

# Send test message (press Ctrl+D to send EOF)
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

### 4. Check in VS Code

1. **Open Settings**:
   - `Cmd+,` (Mac) or `Ctrl+,` (Windows/Linux)
   - Search for "mcp"
   - Ensure "Mcp: Enabled" is checked

2. **List MCP Servers**:
   - `Cmd+Shift+P` → "MCP: List Servers"
   - Look for `pagerduty-viz` with running status

3. **View MCP Logs**:
   - View → Output
   - Select "MCP" from dropdown
   - Check for server startup messages

4. **Test in Chat**:
   - Open Chat panel (`Cmd+I`)
   - Click 🛠️ to see tools
   - Look for `get-incident-dashboard`
   - Send: "Show me incident trends"

## Troubleshooting

### Server not appearing in MCP list

**Check settings file syntax**:
```bash
# Validate JSON
cat mcp-apps/.vscode/settings.json | jq .
# Should output formatted JSON (no errors)
```

**Common issues**:
- Trailing commas in JSON
- Missing quotes around strings
- Incorrect property names (`claude.mcpServers` vs `mcp.servers`)

### "Command not found" errors

**Verify paths exist**:
```bash
# Node.js
ls -la /Users/svillanelo/.nvm/versions/node/v22.22.0/bin/node

# Index.js
ls -la /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/dist/index.js
```

**If node path is different**:
```bash
# Find your actual path
which node

# Update settings.json with your path
```

### Environment variables not working

**VS Code doesn't inherit shell environment** by default.

**Solutions**:

1. **Launch VS Code from terminal** (inherits env):
   ```bash
   code /path/to/workspace
   ```

2. **Use input prompts** (user settings):
   ```json
   "PAGERDUTY_API_KEY": "${input:pagerduty-api-key}"
   ```

3. **Hardcode** (less secure):
   ```json
   "PAGERDUTY_API_KEY": "your-actual-key-here"
   ```

### Server starts but no dashboard

**Check build output**:
```bash
npm run build

# Verify no errors
# Check dist/mcp-app.html exists and is ~759KB
```

**Check MCP logs**:
- View → Output → "MCP"
- Look for:
  - ✅ `Server started successfully`
  - ✅ `Registered tool: get-incident-dashboard`
  - ❌ Any error messages

## Session Development Settings

### Terminal Sessions Active

During this session, the following terminal sessions were active:

**Working Directory**: `/Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps`

**Last Command**: `source /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/.venv/bin/activate`

This shows the Python virtual environment was activated, likely for the main PagerDuty MCP server (Python-based).

### Development Tools Used

- **Node.js**: v22.22.0 (via nvm)
- **Package Manager**: npm (with bun for builds)
- **Build Tools**: Vite, TypeScript, Bun
- **Runtime**: Node.js (for MCP server), React (for UI)
- **Shell**: zsh (macOS default)

## Summary

This VS Code session was configured with:

✅ **Workspace-scoped MCP server** (`claude.mcpServers`)  
✅ **Absolute paths** for Node.js and built server  
✅ **Environment variable integration** for secure API key handling  
✅ **Stdio transport** for MCP protocol communication  
✅ **Node.js v22.22.0** via nvm for modern JavaScript features  

The settings enable seamless integration of the PagerDuty MCP Visualization Server with VS Code's Claude Chat interface, allowing interactive incident dashboards to be displayed directly in the IDE.
