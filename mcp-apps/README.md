# PagerDuty MCP Apps

Interactive React UIs for PagerDuty incident management, embedded in the Python MCP server for seamless IDE integration.

## Architecture

These apps are built as **single-file HTML bundles** using Vite + `vite-plugin-singlefile`, then embedded as MCP resources in the Python server. No separate HTTP servers needed - everything runs through the Python MCP server on stdio.

**Benefits:**
- ✅ Native VS Code integration (MCP resources)
- ✅ Single process, no HTTP server management
- ✅ Direct access to all PagerDuty MCP tools
- ✅ Simple deployment: `uv run pagerduty-mcp`

## Available Apps

### 1. Incident Command Center
Full incident lifecycle management from your IDE:
- Real-time incident feed with auto-refresh
- Deep incident details: timeline, notes, alerts, changes
- Quick actions: acknowledge, resolve
- Escalation UI with policy selection
- AI-powered similar incident detection
- Alert inspection with raw data
- Runbook links parsed from incident metadata

**Usage in VS Code:**
```
Ask Claude: "Show me the incident command center"
```

### 2. On-Call Schedule Visualizer
Who's on-call right now across teams and schedules.

**Usage in VS Code:**
```
Ask Claude: "Show me the on-call schedule"
```

### 3. Service Health Matrix
Service health overview with incident counts and status indicators.

**Usage in VS Code:**
```
Ask Claude: "Show me the service health matrix"
```

### 4. Service Dependency Graph
Interactive graph of service relationships and dependencies.

**Usage in VS Code:**
```
Ask Claude: "Show me the service dependency graph"
```

### 5. Oncall Compensation Report
Per-user on-call hours, incident counts, and interruption rates over a configurable date range.

**Usage in VS Code:**
```
Ask Claude: "Show me the oncall compensation report"
```

### 6. Shift Coverage Wizard
Step-by-step wizard to create schedule overrides:
- Pick a date range and find your on-call shifts
- Select shifts that need coverage
- Choose a coverage user from your schedule
- Confirm and create the override

**Usage in VS Code:**
```
Ask Claude: "Open the shift coverage wizard"
```

### 7. Post-Mortem Builder
Interactive timeline builder for incident post-mortems:
- Search and filter resolved incidents
- Color-coded timeline: triggers, acks, notes, escalations, change events
- Export the full timeline as markdown

**Usage in VS Code:**
```
Ask Claude: "Open the post-mortem builder"
```

### 8. Operations Intelligence Report
Real-time ops metrics dashboard:
- Summary cards: total incidents, high-urgency rate, avg MTTR, on-call users
- Service breakdown table with incident counts and MTTR
- Sortable incident table with team and date-range filtering

**Usage in VS Code:**
```
Ask Claude: "Show me the operations intelligence report"
```

## Development

### Quick Start - Build All Apps

```bash
./build-all.sh
```

This builds all apps and copies them to the Python package.

### Manual Build Process

#### Install Dependencies
```bash
cd incident-command-center && npm install
cd ../oncall-schedule-visualizer && npm install
cd ../service-health-matrix && npm install
cd ../service-dependency-graph && npm install
cd ../oncall-compensation && npm install
cd ../shift-coverage-wizard && npm install
cd ../post-mortem-builder && npm install
cd ../operations-intelligence && npm install
```

#### Build Individual Apps
```bash
cd incident-command-center && npm run build
cd ../oncall-schedule-visualizer && npm run build
cd ../service-health-matrix && npm run build
cd ../service-dependency-graph && npm run build
cd ../oncall-compensation && npm run build
cd ../shift-coverage-wizard && npm run build
cd ../post-mortem-builder && npm run build
cd ../operations-intelligence && npm run build
```

#### Copy to Python Package
```bash
cp incident-command-center/dist/mcp-app.html ../pagerduty_mcp/incident_command_center_view.html
cp oncall-schedule-visualizer/dist/mcp-app.html ../pagerduty_mcp/oncall_schedule_visualizer_view.html
cp service-health-matrix/dist/mcp-app.html ../pagerduty_mcp/service_health_matrix_view.html
cp service-dependency-graph/dist/mcp-app.html ../pagerduty_mcp/service_dependency_graph_view.html
cp oncall-compensation/dist/mcp-app.html ../pagerduty_mcp/oncall_compensation_view.html
cp shift-coverage-wizard/dist/mcp-app.html ../pagerduty_mcp/shift_coverage_wizard_view.html
cp post-mortem-builder/dist/mcp-app.html ../pagerduty_mcp/post_mortem_builder_view.html
cp operations-intelligence/dist/mcp-app.html ../pagerduty_mcp/operations_intelligence_view.html
```

### Test in VS Code

1. **Start the Python MCP server:**
   ```bash
   cd .. && uv run pagerduty-mcp --enable-write-tools
   ```

2. **Configure VS Code** (if not already done):
   Add to your VS Code `settings.json`:
   ```json
   {
     "mcp.servers": {
       "pagerduty": {
         "command": "uv",
         "args": ["run", "pagerduty-mcp", "--enable-write-tools"],
         "cwd": "/path/to/pagerduty-mcp-server",
         "env": {
           "PAGERDUTY_USER_API_KEY": "${input:pagerduty-api-key}"
         }
       }
     }
   }
   ```

3. **Test in Claude Code:**
   - "Show me the incident command center"
   - "Show me the on-call schedule"
   - "Show me the service health matrix"

## How It Works

```
┌─────────────────────────────────────────┐
│          VS Code (Claude)               │
│  ┌───────────────────────────────────┐  │
│  │  Embedded HTML UI (React App)    │  │
│  │  - Calls MCP tools via bridge    │  │
│  └───────────────────────────────────┘  │
│              ↕ MCP Protocol (stdio)     │
│  ┌───────────────────────────────────┐  │
│  │  Python MCP Server                │  │
│  │  - Serves HTML as MCP resource    │  │
│  │  - Provides tools & data          │  │
│  └───────────────────────────────────┘  │
│              ↕ HTTPS API                │
│  ┌───────────────────────────────────┐  │
│  │  PagerDuty API                    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Folder Structure

```
mcp-apps/
├── README.md (this file)
├── build-all.sh (build script for all apps)
├── setup-all.sh (install + build all apps)
│
├── incident-command-center/
├── oncall-schedule-visualizer/
├── service-health-matrix/
├── service-dependency-graph/
├── oncall-compensation/
├── shift-coverage-wizard/
├── post-mortem-builder/
└── operations-intelligence/
    (each follows the same structure:
     package.json, tsconfig.json, vite.config.ts,
     mcp-app.html, src/{mcp-app.tsx,styles.css,api.ts,components/},
     dist/mcp-app.html after build)
```

## Development Workflow

### Making Changes

1. **Edit React components** in `src/`
2. **Build the app**: `npm run build`
3. **Copy to Python**: `cp dist/mcp-app.html ../pagerduty_mcp/{app}_view.html`
4. **Restart Python server**: `uv run pagerduty-mcp --enable-write-tools`
5. **Test in VS Code**: Ask Claude to show the app

### Hot Reload (Development Mode)

```bash
# Watch mode (rebuilds on changes)
cd incident-command-center
npm start
```

Note: You'll still need to manually copy the HTML after builds since the apps are embedded.

## Design System

All apps use a consistent design language:

### Colors
- **Primary**: #4299e1 (blue)
- **Success**: #48bb78 (green)
- **Warning**: #ed8936 (orange)
- **Danger**: #e53e3e (red)
- **Gray**: #718096

### Typography
- **Font**: System fonts (-apple-system, SF Pro, etc.)
- **Headers**: 700 weight
- **Body**: 400 weight
- **Labels**: 500-600 weight

### Spacing
- **Small**: 4-8px
- **Medium**: 12-16px
- **Large**: 20-24px

## Troubleshooting

### App doesn't load in VS Code
- Verify HTML file exists in `pagerduty_mcp/` directory
- Check Python server starts without errors
- Ensure tool names match between React app and Python server

### Data doesn't load
- Verify PagerDuty API token is configured
- Check `--enable-write-tools` flag if using write operations
- Look for errors in Python server logs

### Build fails
- Run `npm install` to ensure dependencies are installed
- Check TypeScript errors: `npm run typecheck`
- Verify `vite-plugin-singlefile` is installed

## Support

- **Issues**: Open issues in the repository
- **Documentation**: See [MCP Apps SDK](https://github.com/modelcontextprotocol/ext-apps)
- **PagerDuty API**: [API Reference](https://developer.pagerduty.com/api-reference/)

## License

MIT
