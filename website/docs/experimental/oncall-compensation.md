---
sidebar_position: 4
---

# On-Call Compensation Report

The **On-Call Compensation Report** is an interactive data table that breaks down on-call burden by person — hours scheduled, incidents responded to, off-hours interruptions, and more. Built on the [MCP Apps extension](https://modelcontextprotocol.io/extensions/apps/overview), it surfaces the data you need for compensation reviews, load balancing conversations, and team health check-ins, all inside your agent chat session.

![On-Call Compensation Report in VS Code](/img/ocr-vscode-full.png)

## What you see

The report opens with a summary row of fleet-wide stats at the top, followed by a sortable table with one row per user.

### Summary cards

| Card | What it shows |
|------|--------------|
| Users On-Call | Total number of users who were on-call in the selected period |
| Total On-Call Hours | Sum of all scheduled on-call hours across all users |
| Incidents Responded | Total incidents, split into high and low urgency |
| Avg Incidents / User | Mean incident count per on-call user |
| Off-Hour Interruptions | Interruptions outside business hours across all users |
| Sleep Interruptions | Interruptions during typical sleep hours across all users |

### Compensation table columns

Each column is toggleable — you can show or hide it using the column picker to focus on what matters for your review:

| Column | Description |
|--------|-------------|
| **User** | Name and team memberships |
| **On-Call Hrs** | Total hours scheduled on-call during the period |
| **Incidents** | Total incidents the user was involved in |
| **High Urgency** | High-urgency incidents assigned to this user |
| **Response Hrs** | Time engaged in incident response (capped at 24h per incident) |
| **Rate /hr** | Interruptions per on-call hour — a higher rate means more frequent paging |
| **Off-Hr Intrs** | Interruptions outside business hours (evenings and early mornings) |
| **Sleep Intrs** | Interruptions during typical sleep hours (~10pm–8am) |
| **BH Intrs** | Interruptions during standard business hours |
| **Outside BH Hrs** | On-call hours outside your configured business hours |
| **Weekend Hrs** | On-call hours on weekend days |
| **Holiday Hrs** | On-call hours on configured holidays |
| **Max Consec. Hrs** | Longest single unbroken stretch of out-of-hours on-call time |
| **Unique Periods** | Number of distinct out-of-hours windows — high count means frequently interrupted |

## What you can do

### Set the date range

Use the date pickers at the top to define the reporting window. The table updates immediately when the range changes.

### Configure business hours

Click the business hours settings to define what counts as "inside" hours for your team — work days, start/end times, and holidays. The outside-hours columns (Weekend Hrs, Holiday Hrs, Outside BH Hrs, etc.) are all derived from this configuration.

![Business hours configuration panel](/img/ocr-bh-config.png)

### Sort and filter

Click any column header to sort by that metric. Use the search box to filter by user name or team. Use the team dropdown to focus on a single team.

### Pick visible columns

Click the column picker to toggle columns on or off. Useful for exporting a focused view to share with managers or HR.

### Drill into a user

Click any row to open the user detail modal. It shows the full breakdown for that person — their schedule shifts, incident list, and out-of-hours periods in detail.

![User detail modal](/img/ocr-user-detail.png)

## How it works

The report calls PagerDuty Analytics tools through the MCP server to fetch on-call schedules and interruption data, then computes the business-hours metrics client-side based on your configuration. It does not write any data to PagerDuty, so `--enable-write-tools` is not required (though it does not hurt to have it enabled).

## Supported clients

| Client | Status |
|--------|--------|
| VS Code (GitHub Copilot) | Supported |
| Claude Desktop | Supported |
| Goose | Supported |

## Try it out

The On-Call Compensation Report is available on the `experimental` branch:

```bash
uvx --from git+https://github.com/PagerDuty/pagerduty-mcp-server@experimental pagerduty-mcp
```

Or clone and run locally:

```bash
git clone -b experimental https://github.com/PagerDuty/pagerduty-mcp-server.git
cd pagerduty-mcp-server
uv run python -m pagerduty_mcp
```

Then ask your agent:

```
Show me the on-call compensation report
```

:::caution
The On-Call Compensation Report is experimental. It may change or break between commits and is not covered by the standard support policy. Run it in non-production environments.
:::

## Feedback

Found a bug or want to request a column? Open a GitHub issue tagged `experimental`:

**[github.com/PagerDuty/pagerduty-mcp-server/issues](https://github.com/PagerDuty/pagerduty-mcp-server/issues)**
