# 🏥 Service Health Matrix

Grid view of PagerDuty services with health indicators, incident counts, and recent changes.

## Features

- 🎯 Grid/list/compact view modes
- 🚦 Color-coded health indicators (Green/Yellow/Red)
- 📊 Incident count badges
- 📝 Recent changes timeline
- 🏷️ Team filtering
- 🔍 Click for detailed service view
- ➕ Quick incident creation
- 🔄 Manual refresh

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

Server will start on http://localhost:3003/mcp

## Testing

### With basic-host

```bash
cd ext-apps/examples/basic-host
SERVERS='["http://localhost:3003/mcp"]' npm start
```

### With Claude

```bash
npx cloudflared tunnel --url http://localhost:3003
```

Add the generated URL as a custom connector, then ask:
"Show me the service health matrix"

## Usage

1. **View Services**: See all services in grid format
2. **Health Indicators**: Color-coded health scores (0-100)
3. **Filter Teams**: Check/uncheck teams to focus
4. **Sort Services**: By health, incidents, name, or changes
5. **View Details**: Click any service for detailed view
6. **See Changes**: View recent deployment/configuration changes
7. **Create Incident**: Quick button to manually trigger incident
8. **Refresh**: Click refresh to update health data

## Health Score Calculation

- **100**: No incidents, all alerts resolved
- **75-99**: Minor issues, mostly resolved
- **50-74**: Active incidents, some unresolved
- **0-49**: Critical state, multiple high-urgency incidents

## Integration

Replace mock data in `server.ts` with actual PagerDuty tools:

```typescript
// Get all services
const services = await callPagerDutyTool("list_services", {
  query_model: {
    teams_ids: args.team_ids
  }
});

// For each service, get health data
for (const service of services.services) {
  // Get incidents
  const incidents = await callPagerDutyTool("list_incidents", {
    query_model: {
      service_ids: [service.id],
      since: getSinceTime(args.time_range),
      limit: 100
    }
  });

  // Get changes
  const changes = await callPagerDutyTool("list_service_change_events", {
    service_id: service.id,
    query_model: {
      since: getSinceTime(args.time_range),
      limit: 10
    }
  });

  // Calculate health score
  service.health_score = calculateHealth(incidents, changes);
}
```

## Architecture

- **Server**: Node.js with Express, MCP SDK
- **Client**: React with TypeScript
- **Visualization**: CSS Grid layout with responsive design
- **Communication**: MCP protocol

## View Modes

- **Grid**: Card-based grid layout (default)
- **List**: Vertical list with detailed info
- **Compact**: Minimal view for many services

## License

MIT
