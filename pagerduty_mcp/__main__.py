from pagerduty_mcp.server import app


def main():
    """Main entry point for the pagerduty-mcp command."""
    print("Starting PagerDuty MCP Server. Use the --enable-write-tools flag to enable write tools.")
    app()


if __name__ == "__main__":
    main()
