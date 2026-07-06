import sys

from pagerduty_mcp.server import app


def main():
    """Main entry point for the pagerduty-mcp command."""
    # STDIO transport reserves stdout for JSON-RPC; diagnostics must go to stderr.
    print(
        "Starting PagerDuty MCP Server. Use the --enable-write-tools flag to enable write tools.",
        file=sys.stderr,
    )
    app()


if __name__ == "__main__":
    main()
