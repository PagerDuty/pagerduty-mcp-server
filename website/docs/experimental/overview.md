---
sidebar_position: 1
---

# Experimental

The **Experimental** section is where the **PagerDuty FDE** team publishes work that is actively being explored, tested, and refined — but is not yet part of the stable release.

Think of it as the lab. Things here may change without notice, break between updates, or eventually graduate into the main server. We share them openly so early adopters can try them, give feedback, and help shape what makes it into production.

## Current Initiatives

### MCP Apps

The first initiative under Experimental is **MCP Apps** — interactive HTML UIs that render directly inside agent chat sessions (VS Code, Claude Desktop, Goose, and other MCP-compatible clients).

MCP Apps work by embedding a sandboxed iframe in the chat interface. The app communicates bidirectionally with the MCP server: it can invoke tools to fetch or mutate data, and the server can push updates back to the UI in real time.

:::tip
MCP Apps is an ecosystem-wide extension to the Model Context Protocol, not a PagerDuty-specific feature. See the [official MCP Apps documentation](https://modelcontextprotocol.io/extensions/apps/overview) for the full spec.
:::

| App | Description |
|-----|-------------|
| [Incident Command Center](./incident-command-center) | An interactive incident management dashboard — view, triage, and act on incidents without leaving your IDE |
| [On-Call Schedule Visualizer](./oncall-schedule-visualizer) | A color-coded calendar of on-call schedules across teams — with timezone support and in-place override creation |
| [On-Call Compensation Report](./oncall-compensation) | A sortable breakdown of on-call burden per person — hours, incidents, off-hours interruptions, and configurable business-hours metrics |
| [Service Dependency Graph](./service-dependency-graph) | An interactive node graph of your service topology — business services, technical services, dependencies, and active incident impact |

## The `experimental` branch

The primary source for experimental work is the **`experimental` branch** of the PagerDuty MCP Server repository:

**[github.com/PagerDuty/pagerduty-mcp-server/tree/experimental](https://github.com/PagerDuty/pagerduty-mcp-server/tree/experimental)**

This branch contains:

- **New tools** under active development, not yet available in the published PyPI package
- **Prototype integrations** exploring new PagerDuty API capabilities
- **Performance experiments** such as alternative context strategies or streaming approaches
- **Configuration experiments** that may inform future flags or options in stable releases

## Running the experimental branch

To run the server from the `experimental` branch directly:

```bash
uvx --from git+https://github.com/PagerDuty/pagerduty-mcp-server@experimental pagerduty-mcp
```

Or clone and run locally:

```bash
git clone -b experimental https://github.com/PagerDuty/pagerduty-mcp-server.git
cd pagerduty-mcp-server
uv run python -m pagerduty_mcp
```

## For early adopters

If you want to try experimental features before they ship:

1. Run from the `experimental` branch using the commands above
2. Expect occasional breaking changes between commits — this is not a stable surface
3. Open issues or discussions on [GitHub](https://github.com/PagerDuty/pagerduty-mcp-server/issues) to share feedback directly with the team
4. Watch the [community streams](../community/streams) where the FDE team often demos experimental work live before it's documented

## Feedback

The experimental branch exists because of community engagement. If something in the `experimental` branch is useful to you — or broken — the best place to say so is a GitHub issue tagged `experimental`.

:::caution
Experimental features are not covered by the standard support policy. Use them in non-production environments and treat them as subject to change at any time.
:::
