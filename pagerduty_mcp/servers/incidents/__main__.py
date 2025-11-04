"""Entry point for PagerDuty Incidents MCP Server."""

from .server import app


def main():
    """Main entry point for pagerduty-incidents command."""
    print("Starting PagerDuty Incidents MCP Server...")
    print("Note: Use --enable-write-tools to enable incident creation and modification.")
    app()


if __name__ == "__main__":
    main()
