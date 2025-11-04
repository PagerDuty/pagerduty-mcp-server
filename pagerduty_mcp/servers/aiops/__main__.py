"""Entry point for PagerDuty AIOps MCP Server."""

from .server import app


def main():
    """Main entry point for pagerduty-aiops command."""
    print("Starting PagerDuty AIOps MCP Server...")
    print("Note: Use --enable-write-tools to enable AIOps configuration changes.")
    app()


if __name__ == "__main__":
    main()
