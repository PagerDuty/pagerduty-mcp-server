
from pagerduty_mcp.context import MCPContextManager

def get_client():
    """Backwards-compatible helper to get the PagerDuty client from the current context."""
    return MCPContextManager.get_client()
