# pagerduty-mcp-server
PagerDuty's official local MCP (Model Context Protocol) server which provides tools to interact with your PagerDuty account directly from your MCP-enabled client.

## Skills

The `skills/` directory contains Claude Code skill files — reusable AI workflows that combine PagerDuty MCP tools with other tools to accomplish complex tasks.

### Available skills

| Skill | Description |
|---|---|
| [`terraform-orchestration`](skills/terraform-orchestration.md) | Convert PagerDuty AI Orchestration recommendations into Terraform HCL matching the customer's existing IaC code |

### Loading a skill in Claude Code

```bash
# Load a skill at the start of a session
/skills/terraform-orchestration checkout-api
```

Skills require the PagerDuty MCP server to be configured. Some skills (like `terraform-orchestration`) also require additional MCP servers — see the skill's **Prerequisites** section for details.
