"""
DEPRECATED: This module is deprecated and will be removed in v2.1.
Use pagerduty_mcp.common.utils instead.

Migration:
    OLD: from pagerduty_mcp.utils import paginate
    NEW: from pagerduty_mcp.common.utils import paginate
"""

import warnings

warnings.warn(
    "Importing from pagerduty_mcp.utils is deprecated. "
    "Use pagerduty_mcp.common.utils instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
from pagerduty_mcp.common.utils import *  # noqa: F403, F401
