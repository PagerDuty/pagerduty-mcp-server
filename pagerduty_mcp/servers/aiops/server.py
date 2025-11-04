"""PagerDuty AIOps MCP Server."""

import typer

from pagerduty_mcp.common import (
    create_pagerduty_server,
    register_read_tools,
    register_write_tools,
)
from .tools import READ_TOOLS, WRITE_TOOLS

INSTRUCTIONS = """
# PagerDuty AIOps MCP Server

This server provides tools for managing PagerDuty's AIOps features:
alert grouping (noise reduction) and event orchestrations (intelligent event routing).

## Available Operations

### Alert Grouping Settings (Noise Reduction)
- **List Alert Grouping Settings**: View all alert grouping configurations
- **Get Alert Grouping Setting**: Get details for specific configuration
- **Create Alert Grouping Setting**: Configure alert grouping rules (requires --enable-write-tools)
- **Update Alert Grouping Setting**: Modify grouping configuration (requires --enable-write-tools)
- **Delete Alert Grouping Setting**: Remove grouping configuration (requires --enable-write-tools)

### Event Orchestrations (Intelligent Routing)
- **List Event Orchestrations**: View all event orchestrations
- **Get Event Orchestration**: Get orchestration details
- **Get Event Orchestration Router**: View router configuration
- **Get Event Orchestration Service**: View service-level orchestration
- **Get Event Orchestration Global**: View global orchestration rules
- **Update Event Orchestration Router**: Modify routing rules (requires --enable-write-tools)
- **Append Router Rule**: Add new routing rule (requires --enable-write-tools)

## Tool Categories
- **Read Tools**: Safe, non-destructive operations for viewing configurations
- **Write Tools**: Operations that modify AIOps configurations (requires --enable-write-tools flag)

## Usage Examples
- "Show me all alert grouping settings"
- "Get the event orchestration configuration for the API service"
- "Create alert grouping to reduce noise from monitoring alerts"
- "Add a routing rule to send database alerts to the DBA team"
- "Update the global event orchestration to filter test events"

## Best Practices
- Test alert grouping rules with sample alerts before enabling
- Review existing routing rules before making changes
- Use intelligent grouping to reduce alert fatigue
- Configure service-level orchestrations for fine-grained control
- Keep global orchestration rules simple and maintainable
"""

app = typer.Typer()


@app.command()
def run(*, enable_write_tools: bool = False):
    """Run the PagerDuty AIOps MCP Server.

    Args:
        enable_write_tools: Enable tools that create or modify AIOps configurations
    """
    mcp = create_pagerduty_server(
        name="PagerDuty AIOps MCP Server",
        instructions=INSTRUCTIONS,
    )

    register_read_tools(mcp, READ_TOOLS)

    if enable_write_tools:
        register_write_tools(mcp, WRITE_TOOLS)

    mcp.run()


if __name__ == "__main__":
    app()
