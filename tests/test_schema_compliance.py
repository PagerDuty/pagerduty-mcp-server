"""Tests verifying MCP tool schema compatibility."""
import asyncio
import json
import unittest


class TestSchemaCompliance(unittest.TestCase):
    """Verify tool schemas are compatible with all MCP clients."""

    @classmethod
    def setUpClass(cls):
        from pagerduty_mcp.server import mcp

        cls.tools = asyncio.run(mcp.list_tools())

    def test_no_ref_or_defs_in_tool_schemas(self):
        """No tool schema should contain $ref or $defs (breaks Copilot/Cursor/Bedrock)."""
        violations = []
        for tool in self.tools:
            schema_str = json.dumps(tool.inputSchema)
            if "$ref" in schema_str or "$defs" in schema_str:
                violations.append(tool.name)
        self.assertEqual(violations, [], msg=f"Tools with $ref/$defs: {violations}")

    def test_total_schema_size_below_threshold(self):
        """Total tool schema JSON should be <150K chars to avoid context bloat."""
        total = sum(len(json.dumps(t.inputSchema)) for t in self.tools)
        self.assertLess(total, 150_000, msg=f"Total schema size {total} chars exceeds 150K limit")
