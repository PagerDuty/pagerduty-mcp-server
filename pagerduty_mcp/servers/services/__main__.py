"""Entry point for PagerDuty Services MCP Server."""

from .server import app


def main():
    """Main entry point for pagerduty-services command."""
    print("Starting PagerDuty Services MCP Server...")
    print("Note: Use --enable-write-tools to enable service creation and modification.")
    app()


if __name__ == "__main__":
    main()
