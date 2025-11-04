"""PagerDuty Services MCP Server."""

import typer

from pagerduty_mcp.common import (
    create_pagerduty_server,
    register_read_tools,
    register_write_tools,
)
from .tools import READ_TOOLS, WRITE_TOOLS

# Server-specific instructions for LLM
INSTRUCTIONS = """
# PagerDuty Services MCP Server

This server provides tools for managing PagerDuty services.

## Available Operations

### Service Discovery
- **List Services**: Browse and search all services with filtering options
- **Get Service Details**: Retrieve comprehensive information about a specific service

### Service Management (Write Tools - requires --enable-write-tools)
- **Create Service**: Create new services with escalation policies and integrations
- **Update Service**: Modify existing service configurations

## Tool Categories
- **Read Tools**: Safe, non-destructive operations for service data retrieval
- **Write Tools**: Operations that create or modify services (requires --enable-write-tools flag)

## Usage Examples
- "Show me all services owned by the database team"
- "Get details for the payment-api service"
- "Create a new service for the authentication microservice"
- "Update the escalation policy for the main-app service"

## Best Practices
- Always verify service details before making modifications
- Ensure escalation policies are properly configured when creating services
- Keep service names descriptive and consistent with your organization's naming convention
"""

# Create Typer app for CLI
app = typer.Typer()


@app.command()
def run(*, enable_write_tools: bool = False):
    """
    Run the PagerDuty Services MCP Server.

    Args:
        enable_write_tools: Enable tools that create or modify services
    """
    # Create server instance
    mcp = create_pagerduty_server(
        name="PagerDuty Services MCP Server",
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
