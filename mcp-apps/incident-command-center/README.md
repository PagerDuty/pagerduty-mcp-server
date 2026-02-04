# 🚨 Incident Command Center

Real-time PagerDuty incident management dashboard with AI-powered insights.

## Features

- ⚡ Real-time incident feed (auto-refresh every 10 seconds)
- ✅ One-click actions (Acknowledge, Resolve, Add Note)
- 🤖 AI-powered similar incident detection
- 🔗 Related incidents graph
- 🎯 Filter by status, urgency, service, team
- 📊 Alert count tracking
- ⏰ Human-readable timestamps

## Installation

```bash
npm install
```

## Development

```bash
# Build and start with hot reload
npm start

# Type check
npm run typecheck
```

## Production

```bash
# Build for production
npm run build

# Run production server
npm run serve
```

Server will start on http://localhost:3001/mcp

## Testing

### With basic-host

```bash
# Clone ext-apps repo if you haven't
git clone https://github.com/modelcontextprotocol/ext-apps.git

# Start basic-host
cd ext-apps/examples/basic-host
npm install
SERVERS='["http://localhost:3001/mcp"]' npm start
```

Navigate to http://localhost:8080

### With Claude

1. Expose server:
   ```bash
   npx cloudflared tunnel --url http://localhost:3001
   ```

2. Add as custom connector in Claude (Settings → Connectors)

3. Ask Claude: "Show me the incident command center"

## Usage

Once the app loads:

1. **View Incidents**: See all active incidents with status badges
2. **Quick Actions**: Click Acknowledge or Resolve buttons
3. **Add Notes**: Click 📝 Note button to add context
4. **View Insights**: Click an incident to see similar and related incidents
5. **Auto-Refresh**: Dashboard updates every 10 seconds automatically

## Architecture

- **Server**: Node.js with Express and MCP SDK
- **Client**: React with TypeScript
- **Bundler**: Vite with single-file plugin
- **Communication**: MCP protocol over postMessage

## Integration

To integrate with actual PagerDuty MCP tools, replace mock data in `server.ts` with:

```typescript
// Instead of mock data, call actual PagerDuty tools
const incidents = await callPagerDutyTool("mcp__pagerduty-mcp-pdt-svillanelo__list_incidents", {
  query_model: {
    status: args.status,
    urgencies: args.urgency,
    service_ids: args.service_ids,
    teams_ids: args.team_ids,
    limit: 50
  }
});
```

## License

MIT
