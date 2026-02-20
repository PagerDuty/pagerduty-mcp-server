
from pagerduty_mcp.context import ContextManager

def get_client():
    """Backwards-compatible helper to get the PagerDuty client from the current context."""
    return ContextManager.get_client()
