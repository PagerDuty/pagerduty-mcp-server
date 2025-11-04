"""Entry point for PagerDuty People MCP Server."""

from .server import app


def main():
    """Main entry point for pagerduty-people command."""
    print("Starting PagerDuty People MCP Server...")
    print("Note: Use --enable-write-tools to enable team/schedule modifications.")
    app()


if __name__ == "__main__":
    main()
