"""
DEPRECATED: This module is deprecated and will be removed in v2.1.
Use pagerduty_mcp.common.client instead.

Migration:
    OLD: from pagerduty_mcp.client import get_client
    NEW: from pagerduty_mcp.common.client import get_client
"""

import warnings

# Backward compatibility - will be removed in v2.1
warnings.warn(
    "Importing from pagerduty_mcp.client is deprecated. "
    "Use pagerduty_mcp.common.client instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
from pagerduty_mcp.common.client import *  # noqa: F403, F401
