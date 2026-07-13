"""Tests verifying MCP tool schema compatibility."""
import asyncio
import json
import unittest


class TestSchemaCompliance(unittest.TestCase):
    """Verify tool schemas are compatible with all MCP clients."""

    @classmethod
    def setUpClass(cls):
        from mcp.server.fastmcp import FastMCP
        from pagerduty_mcp.server import MCP_SERVER_INSTRUCTIONS, add_read_only_tool
        from pagerduty_mcp.tools import read_tools

        _mcp = FastMCP("PagerDuty MCP Server", instructions=MCP_SERVER_INSTRUCTIONS)
        for _tool in read_tools:
            add_read_only_tool(_mcp, _tool)
        cls.tools = asyncio.run(_mcp.list_tools())

    def test_total_schema_size_below_threshold(self):
        """Total tool schema JSON should be <150K chars to avoid context bloat."""
        total = sum(len(json.dumps(t.inputSchema)) for t in self.tools)
        self.assertLess(total, 150_000, msg=f"Total schema size {total} chars exceeds 150K limit")
