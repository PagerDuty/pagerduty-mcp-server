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
ONCALL_SCHEDULE_VISUALIZER_URI = "ui://oncall-schedule-visualizer/calendar.html"
SERVICE_DEPENDENCY_GRAPH_URI = "ui://service-dependency-graph/graph.html"
ONCALL_COMPENSATION_URI = "ui://oncall-compensation/report.html"
SHIFT_COVERAGE_WIZARD_URI = "ui://shift-coverage-wizard/wizard.html"
POST_MORTEM_BUILDER_URI = "ui://post-mortem-builder/builder.html"
OPERATIONS_INTELLIGENCE_URI = "ui://operations-intelligence/dashboard.html"

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


def add_oncall_schedule_visualizer(mcp_instance: FastMCP) -> None:
    """Add On-Call Schedule Visualizer MCP App resource.

    The UI directly calls existing MCP tools:
    - list_schedules, get_schedule
    - list_oncalls, list_schedule_users
    - list_teams, list_users

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": ONCALL_SCHEDULE_VISUALIZER_URI},
            "ui/resourceUri": ONCALL_SCHEDULE_VISUALIZER_URI,
        }
    )
    def oncall_schedule_visualizer() -> list[TextContent]:
        """On-Call Schedule Visualizer - Interactive calendar view.

        Shows who's on-call across teams and schedules. The UI calls existing
        MCP tools (list_schedules, list_oncalls, etc.) to fetch data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="On-Call Schedule Visualizer UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        ONCALL_SCHEDULE_VISUALIZER_URI,
        mime_type="text/html;profile=mcp-app",
        description="On-Call Schedule Visualizer - Interactive calendar view of on-call schedules"
    )
    def oncall_schedule_visualizer_view() -> str:
        """On-Call Schedule Visualizer UI resource."""
        html_path = pathlib.Path(__file__).parent / "oncall_schedule_visualizer_view.html"
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


def add_shift_coverage_wizard(mcp_instance: FastMCP) -> None:
    """Add Shift Coverage Wizard MCP App resource.

    The UI directly calls existing MCP tools:
    - get_user_data
    - list_oncalls, list_schedules, list_schedule_users
    - create_schedule_override

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": SHIFT_COVERAGE_WIZARD_URI},
            "ui/resourceUri": SHIFT_COVERAGE_WIZARD_URI,
        }
    )
    def shift_coverage_wizard() -> list[TextContent]:
        """Shift Coverage Wizard - Interactive wizard for creating schedule overrides.

        Step-by-step wizard to select a date range, pick shifts to cover, choose
        a coverage user, and confirm the override. The UI calls existing MCP tools
        (list_oncalls, list_schedule_users, create_schedule_override, etc.) to fetch
        and write data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Shift Coverage Wizard UI initialized. The UI will call existing MCP tools to fetch and write data."
            )
        ]

    @mcp_instance.resource(
        SHIFT_COVERAGE_WIZARD_URI,
        mime_type="text/html;profile=mcp-app",
        description="Shift Coverage Wizard - Interactive wizard for creating schedule overrides"
    )
    def shift_coverage_wizard_view() -> str:
        """Shift Coverage Wizard UI resource."""
        html_path = pathlib.Path(__file__).parent / "shift_coverage_wizard_view.html"
        return html_path.read_text(encoding="utf-8")


def add_post_mortem_builder(mcp_instance: FastMCP) -> None:
    """Add Post-Mortem Builder MCP App resource.

    The UI directly calls existing MCP tools:
    - list_incidents
    - list_log_entries, list_incident_notes
    - list_incident_change_events, list_alerts_from_incident

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": POST_MORTEM_BUILDER_URI},
            "ui/resourceUri": POST_MORTEM_BUILDER_URI,
        }
    )
    def post_mortem_builder() -> list[TextContent]:
        """Post-Mortem Builder - Interactive timeline builder for incident post-mortems.

        Select a resolved incident and generate a color-coded timeline of events
        including triggers, acknowledgements, notes, escalations, and change events.
        Export the timeline as markdown. The UI calls existing MCP tools to fetch data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Post-Mortem Builder UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        POST_MORTEM_BUILDER_URI,
        mime_type="text/html;profile=mcp-app",
        description="Post-Mortem Builder - Interactive incident timeline builder for post-mortems"
    )
    def post_mortem_builder_view() -> str:
        """Post-Mortem Builder UI resource."""
        html_path = pathlib.Path(__file__).parent / "post_mortem_builder_view.html"
        return html_path.read_text(encoding="utf-8")


def add_operations_intelligence(mcp_instance: FastMCP) -> None:
    """Add Operations Intelligence Report MCP App resource.

    The UI calls these MCP tools:
    - get_incident_metrics_by_service (Analytics API — service-level MTTA/MTTR/escalations)
    - get_incident_metrics_by_team (Analytics API — team-level MTTA/MTTR/escalations)
    - get_responder_load_metrics (Analytics API — responder on-call hours and interruptions)
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

        Two-tab dashboard: Operational (service/team/responder metrics from Analytics API)
        and Insights (AI-powered trend analysis via PagerDuty Advanced MCP insights_agent_tool).

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Operations Intelligence Report UI initialized. The UI will call existing MCP tools to fetch data."
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
    add_oncall_schedule_visualizer(mcp)
    add_service_dependency_graph(mcp)
    add_oncall_compensation(mcp)
    add_shift_coverage_wizard(mcp)
    add_post_mortem_builder(mcp)
    add_operations_intelligence(mcp)

    mcp.run()
