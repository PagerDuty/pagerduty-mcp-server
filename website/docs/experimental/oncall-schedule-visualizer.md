---
sidebar_position: 3
---

# On-Call Schedule Visualizer

The **On-Call Schedule Visualizer** is an interactive calendar that shows who is on-call across all your PagerDuty schedules, rendered directly inside your agent chat session. Built on the [MCP Apps extension](https://modelcontextprotocol.io/extensions/apps/overview), it gives you a clear, color-coded view of on-call coverage without opening the PagerDuty web UI.

![On-Call Schedule Visualizer in VS Code](/img/osv-vscode-full.png)

## What you see

The visualizer opens as a calendar grid — week or month view — with each on-call shift rendered as a color-coded block. Schedules are grouped by team and each team gets a distinct color so coverage gaps and overlaps are immediately visible.

![Calendar grid with color-coded shifts](/img/osv-calendar-grid.png)

Each shift block shows:

- **User name** on the shift
- **Schedule name** it belongs to
- **Start and end times** (in your selected timezone)

Hovering over a shift reveals the full details in a tooltip.

## What you can do

### Switch between week and month view

Toggle between a focused weekly view and a high-level monthly overview depending on how far ahead you need to look.

### Filter by team

Use the team filter panel to show or hide individual teams. Useful when you have many schedules and only care about a subset.

### Change timezone

Select from major US timezones or UTC. All shift times update immediately to reflect the new timezone — no reload needed.

### Create a schedule override

Click on any shift block to open the override modal. Select the replacement user and confirm — the override is created directly through the MCP server without leaving your IDE.

![Schedule override modal](/img/osv-override-modal.png)

## How it works

The On-Call Schedule Visualizer calls `list_schedules` and `list_oncalls` through the PagerDuty MCP Server to fetch current shift data, then renders the calendar grid client-side. Creating an override calls `create_schedule_override` — a write operation that requires `--enable-write-tools`.

## Supported clients

| Client | Status |
|--------|--------|
| VS Code (GitHub Copilot) | Supported |
| Claude Desktop | Supported |
| Goose | Supported |

## Try it out

The On-Call Schedule Visualizer is available on the `experimental` branch. Run the server with write tools enabled to unlock override creation:

```bash
uvx --from git+https://github.com/PagerDuty/pagerduty-mcp-server@experimental pagerduty-mcp --enable-write-tools
```

Or clone and run locally:

```bash
git clone -b experimental https://github.com/PagerDuty/pagerduty-mcp-server.git
cd pagerduty-mcp-server
uv run python -m pagerduty_mcp --enable-write-tools
```

Then ask your agent:

```
Show me the on-call schedule
```

:::caution
The On-Call Schedule Visualizer is experimental. It may change or break between commits and is not covered by the standard support policy. Run it in non-production environments.
:::

## Feedback

Found a bug? Have a feature idea? Open a GitHub issue tagged `experimental`:

**[github.com/PagerDuty/pagerduty-mcp-server/issues](https://github.com/PagerDuty/pagerduty-mcp-server/issues)**
