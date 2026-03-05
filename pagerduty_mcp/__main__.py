from pagerduty_mcp.server import app


def main():
    """Main entry point for the pagerduty-mcp command."""
    print(
        "Starting PagerDuty MCP Server. "
        "Use the --enable-write-tools flag to enable write tools. "
        "Use --disabled-tool-categories to disable specific tool categories."
    )
    app()


if __name__ == "__main__":
    main()
