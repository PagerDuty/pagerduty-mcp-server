# 📅 On-Call Schedule Visualizer

Interactive calendar visualization of PagerDuty on-call schedules.

## Features

- 📅 Week/month calendar views
- 🎨 Color-coded schedules by team
- 🌐 Timezone support (5 major US timezones + UTC)
- 🔧 Click to create schedule overrides
- 🏷️ Team filtering
- 👤 Hover tooltips with user details
- 📱 Responsive mobile design

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

Server will start on http://localhost:3002/mcp

## Testing

### With basic-host

```bash
cd ext-apps/examples/basic-host
SERVERS='["http://localhost:3002/mcp"]' npm start
```

### With Claude

```bash
npx cloudflared tunnel --url http://localhost:3002
```

Add the generated URL as a custom connector in Claude, then ask:
"Show me the on-call calendar"

## Usage

1. **View Schedule**: See who's on-call across all schedules
2. **Switch View**: Toggle between week and month views
3. **Filter Teams**: Check/uncheck teams to focus
4. **Change Timezone**: Select your timezone from dropdown
5. **Create Override**: Click on any shift to create an override
6. **Hover Details**: Hover over shift blocks for full information

## Integration

Replace mock data in `server.ts` with actual PagerDuty tools:

```typescript
// Get schedules
const schedules = await callPagerDutyTool("list_schedules", {
  query_model: {
    team_ids: args.team_ids,
    include: ["schedule_layers"]
  }
});

// Get oncalls
const oncalls = await callPagerDutyTool("list_oncalls", {
  query_model: {
    schedule_ids: args.schedule_ids,
    since: args.since,
    until: args.until,
    time_zone: args.time_zone
  }
});
```

## Architecture

- **Server**: Node.js with Express, MCP SDK
- **Client**: React with TypeScript
- **Visualization**: Custom calendar grid with CSS positioning
- **Communication**: MCP protocol

## License

MIT
