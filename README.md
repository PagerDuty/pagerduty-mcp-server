# PagerDuty's official MCP Server

<!-- mcp-name: io.github.PagerDuty/pagerduty-mcp -->

PagerDuty's local MCP (Model Context Protocol) server which provides tools to interact with your PagerDuty account, allowing you to manage incidents, services, schedules, event orchestrations, and more directly from your MCP-enabled client.

## Quick start

You need [`uv`](https://github.com/astral-sh/uv) and a PagerDuty **User API Token** — see
[Prerequisites](docs/getting-started/prerequisites.md) and [Authentication](docs/getting-started/authentication.md).

```bash
PAGERDUTY_USER_API_KEY="your-token" uvx pagerduty-mcp
```

By default only read-only tools are exposed. Add `--enable-write-tools` to allow tools that modify
your PagerDuty account. Then point your MCP client at the server —
[Cursor](docs/installation/cursor.md), [VS Code](docs/installation/vscode.md),
[Claude Desktop](docs/installation/claude-desktop.md), or [Docker](docs/installation/docker.md).

Prefer no local install? PagerDuty hosts a
[Remote MCP Server](https://support.pagerduty.com/main/docs/pagerduty-mcp-server) with OAuth support.

## Contents

The full documentation lives in [`docs/`](docs/) and is readable directly on GitHub.

**Getting Started**

- [Introduction](docs/intro.md) — what the MCP server is and what it can do
- [Prerequisites](docs/getting-started/prerequisites.md)
- [Quick Start](docs/getting-started/quick-start.md)
- [Authentication](docs/getting-started/authentication.md)

**Installation**

- [Cursor](docs/installation/cursor.md)
- [VS Code](docs/installation/vscode.md)
- [Claude Desktop](docs/installation/claude-desktop.md)
- [Docker](docs/installation/docker.md)

**Remote Server**

- [Remote MCP Server Setup](https://support.pagerduty.com/main/docs/pagerduty-mcp-server) — PagerDuty-hosted,
  no local install. Maintained on the PagerDuty Knowledge Base.

**Configuration**

- [Environment Variables](docs/configuration/environment-variables.md)
- [Transport Modes](docs/configuration/transports.md)
- [Write Tools](docs/configuration/write-tools.md)
- [Tool Filtering](docs/configuration/tool-filtering.md)

**Tools Reference**

- [Tools Overview](docs/tools/overview.md) — every tool, read/write type, and description
- [Alert Grouping](docs/tools/alert-grouping.md)
- [Alerts](docs/tools/alerts.md)
- [Analytics](docs/tools/analytics.md)
- [Business Services](docs/tools/business-services.md)
- [Change Events](docs/tools/change-events.md)
- [Incidents](docs/tools/incidents.md)
- [Incident Workflows](docs/tools/incident-workflows.md)
- [Services](docs/tools/services.md)
- [Teams](docs/tools/teams.md)
- [Users](docs/tools/users.md)
- [Schedules](docs/tools/schedules.md)
- [On-Call](docs/tools/oncalls.md)
- [Priorities](docs/tools/priorities.md)
- [Log Entries](docs/tools/log-entries.md)
- [Escalation Policies](docs/tools/escalation-policies.md)
- [Event Orchestrations](docs/tools/event-orchestrations.md)
- [Status Pages](docs/tools/status-pages.md)

**Use Cases**

- [Use Cases Overview](docs/use-cases/overview.md)
- [Incident Investigation](docs/use-cases/incident-investigation.md)
- [On-Call Handoff](docs/use-cases/on-call-handoff.md)
- [Service Health Check](docs/use-cases/service-health-check.md)
- [Incident Response Automation](docs/use-cases/incident-response-automation.md)

**Experimental**

- [Experimental Overview](docs/experimental/overview.md) — MCP Apps and the `experimental` branch
- [Incident Command Center](docs/experimental/incident-command-center.md)
- [On-Call Manager](docs/experimental/oncall-manager.md)
- [On-Call Compensation Report](docs/experimental/oncall-compensation.md)
- [Service Dependency Graph](docs/experimental/service-dependency-graph.md)
- [Onboarding Wizard](docs/experimental/onboarding-wizard.md)

**Community**

- [Community Streams](docs/community/streams.md)

**Contributing**

- [Development Setup](docs/contributing/development.md)
- [Contributing Guidelines](docs/contributing/guidelines.md)

## Support

PagerDuty's MCP server is an open-source project, and as such, we offer only community-based support. If assistance is required, please open an issue in [GitHub](https://github.com/pagerduty/pagerduty-mcp-server) or [PagerDuty's community forum](https://community.pagerduty.com/).

## Contributing

If you are interested in contributing to this project, please refer to our [Contributing Guidelines](https://github.com/pagerduty/pagerduty-mcp-server/blob/main/CONTRIBUTING.md) and the [development setup guide](docs/contributing/development.md).
