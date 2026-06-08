from pagerduty_mcp.context import ContextResolver


def get_client():
    """Backwards-compatible helper to get the PagerDuty client from the current context."""
    return ContextResolver.get_client()
