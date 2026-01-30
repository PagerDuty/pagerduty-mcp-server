# PagerDuty MCP Visualization Server

Interactive dashboards for PagerDuty incident management using the MCP Apps SDK.

## Features

- **Real-time Incident Dashboard** - Live charts showing incident trends over 24h/7d/30d
- **Service Health Table** - Visual overview of incidents per service with status indicators
- **Urgency Distribution** - Donut chart breakdown of high vs low urgency incidents
- **MTTR Analytics** - Average resolution time tracking per service
- **Auto-polling** - Dashboard updates every 30 seconds with fresh data
- **Recent Incidents** - Live feed of active incidents with status badges

## Prerequisites

- Node.js 18+
- Bun runtime (auto-installed on first build)
- PagerDuty API credentials (read-only access sufficient)

## Installation

```bash
# Clone the repository
git clone https://github.com/svillanelo/pagerduty-mcp-viz-server.git
cd pagerduty-mcp-viz-server

# Install dependencies
npm install

# Build the server
export PATH="$HOME/.bun/bin:$PATH"
npm run build
```

## Configuration

### Environment Variables

Set these environment variables for PagerDuty API access:

```bash
export PAGERDUTY_API_KEY="your-api-key"
export PAGERDUTY_USER_EMAIL="your-email@example.com"
```

### Claude Desktop Configuration

Add this server to your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pagerduty-viz": {
      "command": "node",
      "args": ["/absolute/path/to/pagerduty-mcp-viz-server/dist/index.js", "--stdio"],
      "env": {
        "PAGERDUTY_API_KEY": "your-api-key-here",
        "PAGERDUTY_USER_EMAIL": "your-email@example.com"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/` with the actual path to your cloned repository.

### VS Code Configuration

For VS Code with the Claude extension, add to your workspace settings (`.vscode/settings.json`):

```json
{
  "claude.mcpServers": {
    "pagerduty-viz": {
      "command": "node",
      "args": ["/absolute/path/to/pagerduty-mcp-viz-server/dist/index.js", "--stdio"],
      "env": {
        "PAGERDUTY_API_KEY": "your-api-key-here",
        "PAGERDUTY_USER_EMAIL": "your-email@example.com"
      }
    }
  }
}
```

## Usage

After configuring the server in your MCP client (Claude Desktop or VS Code):

1. **Open the dashboard**:
   ```
   Show me incident trends
   ```
   or
   ```
   Get incident dashboard
   ```

2. **The dashboard displays**:
   - **Summary cards**: Total incidents, active incidents, resolved today, average resolution time
   - **Incident timeline**: Line chart showing triggered/acknowledged/resolved incidents over time
   - **Urgency distribution**: Donut chart showing high vs low urgency breakdown
   - **Service health table**: Top 10 services by incident count with status indicators
   - **Recent active incidents**: Live feed with status and urgency badges

3. **Real-time updates**:
   - Dashboard auto-refreshes every 30 seconds
   - Pause/resume updates with the button in the header
   - Last update timestamp shown
   - Active incidents count updates in real-time

## Development

```bash
# Development mode with hot reload
npm run dev

# Watch mode for UI changes only
npm run watch

# Serve the server with hot reload
npm run serve

# Build for production
npm run build
```

## Architecture

This server follows the MCP Apps SDK **two-tool pattern** from the system-monitor example:

### Tools

1. **get-incident-dashboard** (Model-facing)
   - Called by LLM when user requests visualization
   - Fetches incident and service data from PagerDuty API
   - Aggregates data: time-series, service health, urgency distribution
   - Returns structured data + opens React UI in iframe
   - Provides text summary for the LLM context

2. **poll-incident-stats** (App-only)
   - Called by React app every 30 seconds via `setInterval`
   - Returns real-time active incident metrics
   - Hidden from LLM (`_meta.ui.visibility: ["app"]`)
   - Lightweight: only dynamic data, no full refetch

### Data Flow

```
User asks Claude → "Show me incident trends"
                 ↓
Claude calls → get-incident-dashboard tool
             ↓
Server fetches → PagerDuty API (list_incidents, list_services)
               ↓
Server aggregates → Time-series buckets, service grouping, MTTR calc
                  ↓
Returns to UI → Structured data + opens React dashboard iframe
              ↓
React app polls → poll-incident-stats every 30s
                ↓
Charts update → Chart.js renders, smooth animations
```

### Caching Strategy

To respect PagerDuty API rate limits (960 requests/min):

- **Incident data**: 30 second TTL
- **Service data**: 5 minute TTL (services change infrequently)
- **Aggregated metrics**: 60 second TTL

**Estimated load**: ~120 API requests/hour (well under limit)

## Project Structure

```
pagerduty-mcp-viz-server/
├── server.ts                    # MCP server (tool registration)
├── main.ts                      # HTTP server for development
├── lib/
│   ├── schemas.ts               # Zod schemas + TypeScript types
│   ├── pagerduty-client.ts      # PagerDuty REST API wrapper
│   ├── cache.ts                 # Server-side TTL cache
│   └── aggregations.ts          # Time-series, MTTR calculations
├── src/
│   ├── mcp-app.tsx              # React dashboard component
│   ├── mcp-app.html             # HTML template
│   └── global.css               # Global styles
└── dist/                        # Build output
    ├── mcp-app.html             # Bundled UI (single 759KB file)
    ├── server.js                # Compiled server logic
    └── index.js                 # CLI entry point with shebang
```

## Tech Stack

- **Backend**: TypeScript + Node.js
- **Frontend**: React 19 + Chart.js 4.4
- **MCP SDK**: @modelcontextprotocol/ext-apps (MCP Apps standard)
- **Build**: Vite (UI bundling) + Bun (server bundling)
- **Validation**: Zod schemas for type-safe data

## How It Works

This implementation follows the official MCP Apps specification:

1. **Server registers tool + resource**:
   ```typescript
   registerAppTool(server, "get-incident-dashboard", {
     _meta: { ui: { resourceUri: "ui://incident-dashboard/mcp-app.html" } }
   });
   registerAppResource(server, resourceUri, ...);
   ```

2. **Host (Claude Desktop) calls tool**:
   - Reads `_meta.ui.resourceUri` from tool definition
   - Fetches HTML resource via MCP protocol
   - Creates sandboxed iframe and loads HTML

3. **React app initializes**:
   ```typescript
   const { app } = useApp({ ... });
   app.ontoolresult = (result) => {
     setDashboardData(result.structuredContent);
   };
   ```

4. **App polls for updates**:
   ```typescript
   setInterval(() => {
     app.callServerTool({ name: "poll-incident-stats" });
   }, 30000);
   ```

## Troubleshooting

### "Missing PagerDuty credentials"

Ensure environment variables are set in your MCP client config:
```json
"env": {
  "PAGERDUTY_API_KEY": "your-key",
  "PAGERDUTY_USER_EMAIL": "your-email"
}
```

### Dashboard not loading

1. Verify build succeeded: `ls -la dist/mcp-app.html dist/index.js`
2. Check path in MCP config is absolute (not relative)
3. Restart Claude Desktop after config changes
4. Check Claude Desktop logs: `~/Library/Logs/Claude/` (macOS)

### No data showing

1. Verify PagerDuty API key has read permissions
2. Check that incidents exist in your PagerDuty account
3. Open browser DevTools in the iframe (right-click → Inspect)
4. Check console for API errors

### Charts not updating

1. Check browser console for polling errors
2. Verify PagerDuty API connectivity
3. Check if caching is working (look for `[Cache HIT]` logs)
4. Ensure polling is not paused (button should show "⏸ Pause Updates")

### Build errors

If `bun: command not found`:
```bash
# Install bun
curl -fsSL https://bun.sh/install | bash

# Add to PATH
export PATH="$HOME/.bun/bin:$PATH"

# Try building again
npm run build
```

## Future Enhancements

- [ ] Time range selector in UI (switch between 24h/7d/30d)
- [ ] Service filtering (focus on specific services)
- [ ] MTTR trend chart with historical data
- [ ] On-call schedule visualization
- [ ] Alert intelligence (top noisy services)
- [ ] Export dashboard as PNG/PDF
- [ ] Responsive mobile layout
- [ ] Incident drill-down (click to see details)

## License

MIT

## Based On

Built using the [MCP Apps SDK](https://github.com/modelcontextprotocol/ext-apps) following patterns from:
- `system-monitor-server` - Two-tool polling pattern
- `budget-allocator-server` - Chart.js integration
- `scenario-modeler-server` - Dashboard layout
- `cohort-heatmap-server` - React components
