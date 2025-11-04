"""PagerDuty Incidents MCP Server."""

import typer

from pagerduty_mcp.common import (
    create_pagerduty_server,
    register_read_tools,
    register_write_tools,
)
from .tools import READ_TOOLS, WRITE_TOOLS

# Server-specific instructions for LLM
INSTRUCTIONS = """
# PagerDuty Incidents MCP Server

This server provides tools for managing PagerDuty incidents.

## Available Operations

### Incident Viewing and Analysis
- **List Incidents**: Search and filter incidents by status, urgency, teams, and more
- **Get Incident Details**: Retrieve comprehensive information about specific incidents
- **Get Outlier Incidents**: Find unusual incidents that deviate from normal patterns
- **Get Past Incidents**: Query historical incidents for analysis
- **Get Related Incidents**: Discover incidents related to a specific incident

### Incident Management (Write Tools - requires --enable-write-tools)
- **Create Incident**: Create new incidents manually
- **Manage Incidents**: Update incident status (acknowledge, resolve, escalate)
- **Add Responders**: Add responders to active incidents
- **Add Notes**: Add notes and comments to incidents

## Tool Categories
- **Read Tools**: Safe, non-destructive operations for incident data retrieval
- **Write Tools**: Operations that create or modify incidents (requires --enable-write-tools flag)

## Usage Examples
- "Show me all high-urgency incidents from the last 24 hours"
- "What are the outlier incidents compared to historical patterns?"
- "Get details for incident INC-123"
- "Create a new incident for database connection issues"
- "Add Jane Doe as a responder to this incident"

## Best Practices
- Always check incident details before making modifications
- Use appropriate urgency levels when creating incidents
- Add context in notes when making changes
- Review related incidents for patterns
"""

# Create Typer app for CLI
app = typer.Typer()


@app.command()
def run(*, enable_write_tools: bool = False):
    """
    Run the PagerDuty Incidents MCP Server.

    Args:
        enable_write_tools: Enable tools that create or modify incidents
    """
    # Create server instance
    mcp = create_pagerduty_server(
        name="PagerDuty Incidents MCP Server",
        instructions=INSTRUCTIONS,
    )

    # Register read tools (always enabled)
    register_read_tools(mcp, READ_TOOLS)

    # Register write tools (conditional)
    if enable_write_tools:
        register_write_tools(mcp, WRITE_TOOLS)

    # Run the server
    mcp.run()


if __name__ == "__main__":
    app()
