import warnings

from pagerduty_mcp.server import app


def main():
    """Main entry point for the pagerduty-mcp command."""
    # Show deprecation warning
    warnings.warn(
        "\n" + "=" * 80 + "\n"
        "DEPRECATION WARNING: The monolithic 'pagerduty-mcp' command is deprecated.\n"
        "\n"
        "Please migrate to the new independent servers (v2.0):\n"
        "  - pagerduty-incidents: Incident management (9 tools)\n"
        "  - pagerduty-services: Service configuration (4 tools)\n"
        "  - pagerduty-people: Teams, users, schedules (17 tools)\n"
        "  - pagerduty-aiops: Alert grouping & event orchestrations (12 tools)\n"
        "\n"
        "Benefits: Smaller contexts, granular control, better LLM performance.\n"
        "\n"
        "The monolithic server will be removed in v2.1.\n"
        "See README.md for migration instructions.\n"
        + "=" * 80,
        DeprecationWarning,
        stacklevel=2,
    )

    print("Starting PagerDuty MCP Server (DEPRECATED - use independent servers).")
    print("Use the --enable-write-tools flag to enable write tools.")
    app()


if __name__ == "__main__":
    main()
