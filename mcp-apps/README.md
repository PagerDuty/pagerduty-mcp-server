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

> **Screenshot:** _Add screenshot here — `docs/screenshots/incident-command-center.png`_
> **Modal:** _Add override/escalation modal screenshot — `docs/screenshots/incident-command-center-modal.png`_

### 2. On-Call Manager
Schedule management with override CRUD and coverage UI:
- View on-call rotations across all schedules
- Create, edit, and delete schedule overrides via modals
- Escalation policy management

**Usage in VS Code:**
```
Ask Claude: "Show me the on-call manager"
```

> **Screenshot:** _Add screenshot here — `docs/screenshots/oncall-manager.png`_
> **Modal:** _Add override creation modal screenshot — `docs/screenshots/oncall-manager-override-modal.png`_

### 3. On-Call Compensation Report
Per-user on-call metrics with compliance and fairness tracking:
- Hours worked, incident counts, interruption rates
- Business hours vs. off-hours breakdown
- Compliance status (EU Working Time Directive)
- Fairness/equity scoring
- CSV export and forward-mode projections

**Usage in VS Code:**
```
Ask Claude: "Show me the oncall compensation report"
```

> **Screenshot:** _Add screenshot here — `docs/screenshots/oncall-compensation.png`_
> **Tab views:** _Add Compliance and Fairness tab screenshots — `docs/screenshots/oncall-compensation-compliance.png`, `docs/screenshots/oncall-compensation-fairness.png`_

### 4. Service Dependency Graph
Interactive graph of service relationships and dependencies.

**Usage in VS Code:**
```
Ask Claude: "Show me the service dependency graph"
```

> **Screenshot:** _Add screenshot here — `docs/screenshots/service-dependency-graph.png`_
> **Impact sidebar:** _Add impact sidebar screenshot — `docs/screenshots/service-dependency-graph-sidebar.png`_

### 5. Onboarding Wizard
Step-by-step wizard for initial PagerDuty account setup:
- Team creation and user invitations
- Schedule configuration with timezone support
- Escalation policy setup
- Service creation with AIOps/alert grouping
- Incident workflow configuration

**Usage in VS Code:**
```
Ask Claude: "Open the onboarding wizard"
```

> **Screenshot:** _Add wizard step screenshots — `docs/screenshots/onboarding-wizard-step1.png` through `docs/screenshots/onboarding-wizard-step6.png`_
> **Best practices panel:** _Add best practices panel screenshot — `docs/screenshots/onboarding-wizard-best-practices.png`_

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
cd ../oncall-manager && npm install
cd ../oncall-compensation && npm install
cd ../service-dependency-graph && npm install
cd ../onboarding-wizard && npm install
```

#### Build Individual Apps
```bash
cd incident-command-center && npm run build
cd ../oncall-manager && npm run build
cd ../oncall-compensation && npm run build
cd ../service-dependency-graph && npm run build
cd ../onboarding-wizard && npm run build
```

#### Copy to Python Package
```bash
cp incident-command-center/dist/mcp-app.html ../pagerduty_mcp/incident_command_center_view.html
cp oncall-manager/dist/mcp-app.html ../pagerduty_mcp/oncall_manager_view.html
cp oncall-compensation/dist/mcp-app.html ../pagerduty_mcp/oncall_compensation_view.html
cp service-dependency-graph/dist/mcp-app.html ../pagerduty_mcp/service_dependency_graph_view.html
cp onboarding-wizard/dist/mcp-app.html ../pagerduty_mcp/onboarding_wizard_view.html
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
   - "Show me the on-call manager"
   - "Show me the oncall compensation report"
   - "Show me the service dependency graph"
   - "Open the onboarding wizard"

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
├── oncall-manager/
├── oncall-compensation/
├── service-dependency-graph/
└── onboarding-wizard/
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
