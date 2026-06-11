---
sidebar_position: 1
slug: /
---

# PagerDuty MCP Server

The **PagerDuty MCP Server** is PagerDuty's official implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — a standard that enables AI assistants to interact with external services through structured tool calls.

With the PagerDuty MCP Server, you can manage your PagerDuty account directly from AI clients like **Cursor**, **VS Code**, **Claude Desktop**, and any other MCP-compatible client.

## What You Can Do

- **Investigate incidents** — list, filter, and get detailed information about active and past incidents
- **Manage on-call schedules** — view schedules, overrides, and who is currently on-call
- **Configure services and teams** — read and update service configurations and team membership
- **Orchestrate events** — inspect and update event orchestration rules
- **Monitor status pages** — read and publish status page updates
- **And 50+ more tools** across 14 PagerDuty domains

## Two Deployment Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Local Server** | Runs on your machine via `uvx` or Docker | Development, personal use, custom configuration |
| **Remote Server** | PagerDuty-hosted, OAuth-based | Teams, zero-install setup, enterprise |

## Tool Summary

The server exposes **55 tools** across **14 domains**:

| Domain | Tools | Write Operations |
|--------|-------|-----------------|
| Alert Grouping | 5 | create, update, delete |
| Alerts | 2 | — |
| Change Events | 4 | — |
| Incidents | 10 | create, manage, add responders, add notes |
| Incident Workflows | 3 | start |
| Services | 4 | create, update |
| Teams | 8 | create, update, delete, add/remove members |
| Users | 2 | — |
| Schedules | 6 | create, update, overrides |
| On-Call | 1 | — |
| Log Entries | 2 | — |
| Escalation Policies | 2 | — |
| Event Orchestrations | 7 | update router, append rules |
| Status Pages | 8 | create posts and updates |

Read-only tools are always available. Write tools require the `--enable-write-tools` flag.

## Quick Navigation

- [Prerequisites](/docs/getting-started/prerequisites) — what you need before starting
- [Quick Start](/docs/getting-started/quick-start) — up and running in 5 minutes
- [Tool Filtering](/docs/configuration/tool-filtering) — reduce tools exposed to your AI client
- [Tools Reference](/docs/tools/overview) — complete tool catalog
