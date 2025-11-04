"""PagerDuty People MCP Server."""

import typer

from pagerduty_mcp.common import (
    create_pagerduty_server,
    register_read_tools,
    register_write_tools,
)

from .tools import READ_TOOLS, WRITE_TOOLS

INSTRUCTIONS = """
# PagerDuty People MCP Server

This server provides tools for managing people-related resources in PagerDuty:
users, teams, schedules, on-call shifts, and escalation policies.

## Available Operations

### User Management
- **Get User Data**: Retrieve information about a specific user
- **List Users**: View all users with filtering options

### Team Management
- **List Teams**: View all teams
- **Get Team**: Get detailed team information
- **List Team Members**: View members of a team
- **Create Team**: Create new teams (requires --enable-write-tools)
- **Update Team**: Modify team configuration (requires --enable-write-tools)
- **Delete Team**: Remove teams (requires --enable-write-tools)
- **Add Team Member**: Add users to teams (requires --enable-write-tools)
- **Remove Team Member**: Remove users from teams (requires --enable-write-tools)

### Schedule Management
- **List Schedules**: View all on-call schedules
- **Get Schedule**: Get detailed schedule information
- **List Schedule Users**: View users in a schedule
- **Create Schedule Override**: Create temporary schedule overrides (requires --enable-write-tools)

### On-Call Management
- **List On-Calls**: View current on-call assignments across schedules and escalation policies

### Escalation Policy Management
- **List Escalation Policies**: View all escalation policies
- **Get Escalation Policy**: Get detailed policy information

## Tool Categories
- **Read Tools**: Safe, non-destructive operations for data retrieval
- **Write Tools**: Operations that create or modify resources (requires --enable-write-tools flag)

## Usage Examples
- "Who is currently on-call for the database team?"
- "List all members of the SRE team"
- "Create a schedule override for next week when I'm on vacation"
- "Add John Doe to the infrastructure team"
- "Show me all escalation policies"

## Best Practices
- Review team membership before making changes
- Use schedule overrides for temporary changes
- Verify on-call assignments after changes
- Keep escalation policies up to date with team changes
"""

app = typer.Typer()


@app.command()
def run(*, enable_write_tools: bool = False):
    """Run the PagerDuty People MCP Server."""
    mcp = create_pagerduty_server(
        name="PagerDuty People MCP Server",
        instructions=INSTRUCTIONS,
    )

    register_read_tools(mcp, READ_TOOLS)

    if enable_write_tools:
        register_write_tools(mcp, WRITE_TOOLS)

    mcp.run()


if __name__ == "__main__":
    app()
