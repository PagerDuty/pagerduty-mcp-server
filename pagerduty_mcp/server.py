import json
import logging
import pathlib
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime

import typer
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations, TextContent

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import MCPContext
from pagerduty_mcp.tools import read_tools, write_tools
from pagerduty_mcp.utils import get_mcp_context

logging.basicConfig(level=logging.WARNING)


app = typer.Typer()

# MCP App URIs
INCIDENT_COMMAND_CENTER_URI = "ui://incident-command-center/dashboard.html"
SERVICE_DEPENDENCY_GRAPH_URI = "ui://service-dependency-graph/graph.html"
ONCALL_COMPENSATION_URI = "ui://oncall-compensation/report.html"
OPERATIONS_INTELLIGENCE_URI = "ui://operations-intelligence/dashboard.html"
ONCALL_MANAGER_URI = "ui://oncall-manager/dashboard.html"

MCP_SERVER_INSTRUCTIONS = """
When the user asks for information about their resources, first get the user data and scope any
requests using the user id.

READ operations are safe to use, but be cautious with WRITE operations as they can modify the
live environment. Always confirm with the user before using any tool marked as destructive.
"""


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:
    """Lifespan context manager for the MCP server.

    Args:
        server: The MCP server instance
    Returns:
        An asynchronous iterator yielding the MCP context.
    """
    try:
        yield get_mcp_context(client=get_client())
    finally:
        pass


def add_read_only_tool(mcp_instance: FastMCP, tool: Callable) -> None:
    """Add a read-only tool with appropriate safety annotations.

    Args:
        mcp_instance: The MCP server instance
        tool: The tool function to add
    """
    mcp_instance.add_tool(
        tool,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True),
    )


def add_write_tool(mcp_instance: FastMCP, tool: Callable) -> None:
    """Add a write tool with appropriate safety annotations that indicate it's dangerous.

    Args:
        mcp_instance: The MCP server instance
        tool: The tool function to add
    """
    mcp_instance.add_tool(
        tool,
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False),
    )


def add_incident_command_center(mcp_instance: FastMCP) -> None:
    """Add Incident Command Center MCP App resource.

    The UI directly calls existing MCP tools:
    - list_incidents, get_incident, list_incident_notes
    - list_alerts_from_incident, list_incident_change_events
    - manage_incidents, add_note_to_incident
    - get_past_incidents, get_related_incidents
    - list_escalation_policies

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": INCIDENT_COMMAND_CENTER_URI},
            "ui/resourceUri": INCIDENT_COMMAND_CENTER_URI,
        }
    )
    def incident_command_center() -> list[TextContent]:
        """Incident Command Center - Interactive incident management dashboard.

        Full incident lifecycle management from your IDE. The UI calls existing
        MCP tools (list_incidents, manage_incidents, etc.) to fetch and manipulate data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Incident Command Center UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        INCIDENT_COMMAND_CENTER_URI,
        mime_type="text/html;profile=mcp-app",
        description="Incident Command Center - Interactive incident management UI"
    )
    def incident_command_center_view() -> str:
        """Incident Command Center UI resource."""
        html_path = pathlib.Path(__file__).parent / "incident_command_center_view.html"
        return html_path.read_text(encoding="utf-8")


def add_service_dependency_graph(mcp_instance: FastMCP) -> None:
    """Add Service Dependency Graph MCP App resource.

    The UI directly calls existing MCP tools:
    - list_services
    - list_service_change_events

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": SERVICE_DEPENDENCY_GRAPH_URI},
            "ui/resourceUri": SERVICE_DEPENDENCY_GRAPH_URI,
        }
    )
    def service_dependency_graph() -> list[TextContent]:
        """Service Dependency Graph - Interactive graph of service dependencies.

        Shows services and their relationships. The UI calls existing
        MCP tools (list_services, etc.) to fetch data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Service Dependency Graph UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        SERVICE_DEPENDENCY_GRAPH_URI,
        mime_type="text/html;profile=mcp-app",
        description="Service Dependency Graph - Interactive graph of service dependencies"
    )
    def service_dependency_graph_view() -> str:
        """Service Dependency Graph UI resource."""
        html_path = pathlib.Path(__file__).parent / "service_dependency_graph_view.html"
        return html_path.read_text(encoding="utf-8")


def add_oncall_compensation(mcp_instance: FastMCP) -> None:
    """Add Oncall Compensation Report MCP App resource.

    The UI directly calls existing MCP tools:
    - list_users, list_teams
    - list_schedules, list_oncalls
    - list_incidents

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": ONCALL_COMPENSATION_URI},
            "ui/resourceUri": ONCALL_COMPENSATION_URI,
        }
    )
    def oncall_compensation() -> list[TextContent]:
        """Oncall Compensation Report - Shows per-user oncall hours and incident stats.

        Shows per-user oncall hours, incident count, incident response hours,
        and interruption rate over a configurable date range.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Oncall Compensation Report UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        ONCALL_COMPENSATION_URI,
        mime_type="text/html;profile=mcp-app",
        description="Oncall Compensation Report - Interactive report of on-call compensation"
    )
    def oncall_compensation_view() -> str:
        """Oncall Compensation Report UI resource."""
        html_path = pathlib.Path(__file__).parent / "oncall_compensation_view.html"
        return html_path.read_text(encoding="utf-8")


def add_operations_intelligence(mcp_instance: FastMCP) -> None:
    """Add Operations Intelligence Report MCP App resource.

    The UI calls these MCP tools:
    - get_incident_metrics_by_service (Analytics API — service-level MTTA/MTTR/escalations)
    - get_incident_metrics_by_team (Analytics API — team-level MTTA/MTTR/escalations/interruptions)
    - get_responder_load_metrics (Analytics API — responder on-call hours, interruptions, and fatigue)
    - get_incident_metrics_all (Analytics API — full-period rollup with P50/P75/P90/P95 percentiles)
    - list_teams (for team picker filter)
    - insights_agent_tool on pagerduty-advance-mcp (AI-powered insights tab)

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": OPERATIONS_INTELLIGENCE_URI},
            "ui/resourceUri": OPERATIONS_INTELLIGENCE_URI,
        }
    )
    def operations_intelligence() -> list[TextContent]:
        """Operations Intelligence Report - Compact PagerDuty Insights dashboard.

        Three-tab dashboard: Operational (service/team/responder metrics from Analytics API with P50-P95 percentiles),
        Team Health (responder fatigue indicators — sleep interruptions, off-hour load, engagement, and risk badges),
        and Insights (AI-powered trend analysis via PagerDuty Advanced MCP insights_agent_tool).

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Operations Intelligence Report UI initialized. The UI calls get_incident_metrics_by_service, get_incident_metrics_by_team, get_responder_load_metrics, get_incident_metrics_all, list_teams, and insights_agent_tool (via pagerduty-advance-mcp) to power the three-tab dashboard (Operational, Team Health, Insights)."
            )
        ]

    @mcp_instance.resource(
        OPERATIONS_INTELLIGENCE_URI,
        mime_type="text/html;profile=mcp-app",
        description="Operations Intelligence Report - Real-time operations metrics and incident analytics"
    )
    def operations_intelligence_view() -> str:
        """Operations Intelligence Report UI resource."""
        html_path = pathlib.Path(__file__).parent / "operations_intelligence_view.html"
        return html_path.read_text(encoding="utf-8")


def add_oncall_manager(mcp_instance: FastMCP) -> None:
    """Add On-Call Manager MCP App resource.

    The UI directly calls existing MCP tools:
    - get_user_data
    - list_oncalls, list_schedules, list_schedule_users
    - create_schedule_override

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": ONCALL_MANAGER_URI},
            "ui/resourceUri": ONCALL_MANAGER_URI,
        }
    )
    def oncall_manager() -> list[TextContent]:
        """On-Call Manager - Personal schedule and override management.

        Shows the current user's upcoming 7-day shifts with countdown cards,
        a 7-day schedule grid, and an Overrides tab with create/coverage wizard.
        The UI calls get_user_data, list_oncalls, list_schedules, list_schedule_users,
        and create_schedule_override.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="On-Call Manager UI initialized. The UI will call existing MCP tools to fetch and write data."
            )
        ]

    @mcp_instance.resource(
        ONCALL_MANAGER_URI,
        mime_type="text/html;profile=mcp-app",
        description="On-Call Manager - Personal schedule view and override management"
    )
    def oncall_manager_view() -> str:
        """On-Call Manager UI resource."""
        html_path = pathlib.Path(__file__).parent / "oncall_manager_view.html"
        return html_path.read_text(encoding="utf-8")


@app.command()
def run(*, enable_write_tools: bool = False) -> None:
    """Run the MCP server with the specified configuration.

    Args:
        enable_write_tools: Flag to enable write tools
    """
    mcp = FastMCP(
        "PagerDuty MCP Server",
        lifespan=app_lifespan,
        instructions=MCP_SERVER_INSTRUCTIONS,
    )
    for tool in read_tools:
        add_read_only_tool(mcp, tool)

    if enable_write_tools:
        for tool in write_tools:
            add_write_tool(mcp, tool)

    # Add MCP Apps
    add_incident_command_center(mcp)
    add_service_dependency_graph(mcp)
    add_oncall_compensation(mcp)
    add_operations_intelligence(mcp)
    add_oncall_manager(mcp)

    mcp.run()
