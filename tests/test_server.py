import unittest
from unittest.mock import MagicMock, patch

import typer

from pagerduty_mcp.server import _parse_disabled_categories, run
from pagerduty_mcp.tools import TOOL_CATEGORIES, VALID_CATEGORIES


class TestParseDisabledCategories(unittest.TestCase):
    """Test cases for _parse_disabled_categories helper."""

    def test_none_returns_empty_set(self):
        """Test that None input returns an empty set."""
        result = _parse_disabled_categories(None)
        self.assertEqual(result, set())

    def test_empty_string_returns_empty_set(self):
        """Test that empty string returns an empty set."""
        result = _parse_disabled_categories("")
        self.assertEqual(result, set())

    def test_single_valid_category(self):
        """Test parsing a single valid category."""
        result = _parse_disabled_categories("alerts")
        self.assertEqual(result, {"alerts"})

    def test_multiple_valid_categories(self):
        """Test parsing multiple valid categories."""
        result = _parse_disabled_categories("alerts,incidents,teams")
        self.assertEqual(result, {"alerts", "incidents", "teams"})

    def test_whitespace_trimmed(self):
        """Test that whitespace around category names is trimmed."""
        result = _parse_disabled_categories("  alerts , incidents , teams  ")
        self.assertEqual(result, {"alerts", "incidents", "teams"})

    def test_trailing_comma_ignored(self):
        """Test that trailing commas are handled gracefully."""
        result = _parse_disabled_categories("alerts,incidents,")
        self.assertEqual(result, {"alerts", "incidents"})

    def test_invalid_category_raises_bad_parameter(self):
        """Test that invalid category names raise typer.BadParameter."""
        with self.assertRaises(typer.BadParameter) as ctx:
            _parse_disabled_categories("bogus")
        self.assertIn("bogus", str(ctx.exception))
        self.assertIn("Valid categories are:", str(ctx.exception))

    def test_mix_valid_and_invalid_raises_bad_parameter(self):
        """Test that a mix of valid and invalid raises typer.BadParameter."""
        with self.assertRaises(typer.BadParameter) as ctx:
            _parse_disabled_categories("alerts,bogus,fake")
        self.assertIn("bogus", str(ctx.exception))
        self.assertIn("fake", str(ctx.exception))

    def test_all_valid_categories_accepted(self):
        """Test that every valid category is accepted."""
        all_cats = ",".join(sorted(VALID_CATEGORIES))
        result = _parse_disabled_categories(all_cats)
        self.assertEqual(result, VALID_CATEGORIES)


class TestValidCategories(unittest.TestCase):
    """Test that VALID_CATEGORIES matches TOOL_CATEGORIES keys."""

    def test_valid_categories_matches_tool_categories(self):
        """Test that VALID_CATEGORIES is exactly the keys of TOOL_CATEGORIES."""
        self.assertEqual(VALID_CATEGORIES, frozenset(TOOL_CATEGORIES.keys()))

    def test_expected_categories_present(self):
        """Test that all 14 expected categories are present."""
        expected = {
            "alert_grouping",
            "alerts",
            "change_events",
            "escalation_policies",
            "event_orchestrations",
            "incident_workflows",
            "incidents",
            "log_entries",
            "oncalls",
            "schedules",
            "services",
            "status_pages",
            "teams",
            "users",
        }
        self.assertEqual(VALID_CATEGORIES, frozenset(expected))


@patch("pagerduty_mcp.server.ApplicationContextStrategy")
class TestToolRegistration(unittest.TestCase):
    """Test tool registration filtering in the run() function."""

    def _count_tools_in_categories(self, category_names, tool_type):
        """Count tools of a given type across specified categories."""
        count = 0
        for name in category_names:
            count += len(TOOL_CATEGORIES[name][tool_type])
        return count

    @patch("pagerduty_mcp.server.FastMCP")
    def test_default_registers_all_read_tools(self, mock_fastmcp_class, _mock_strategy):
        """Test that default config registers all read tools."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        mock_mcp.run = MagicMock()

        run(enable_write_tools=False, disabled_tool_categories=None)

        expected_read_count = self._count_tools_in_categories(VALID_CATEGORIES, "read")
        self.assertEqual(mock_mcp.add_tool.call_count, expected_read_count)

    @patch("pagerduty_mcp.server.FastMCP")
    def test_write_tools_enabled_registers_all(self, mock_fastmcp_class, _mock_strategy):
        """Test that enabling write tools registers all read + write tools."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        mock_mcp.run = MagicMock()

        run(enable_write_tools=True, disabled_tool_categories=None)

        expected_read = self._count_tools_in_categories(VALID_CATEGORIES, "read")
        expected_write = self._count_tools_in_categories(VALID_CATEGORIES, "write")
        self.assertEqual(mock_mcp.add_tool.call_count, expected_read + expected_write)

    @patch("pagerduty_mcp.server.FastMCP")
    def test_disabled_category_excludes_tools(self, mock_fastmcp_class, _mock_strategy):
        """Test that disabling a category excludes its tools."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        mock_mcp.run = MagicMock()

        run(enable_write_tools=True, disabled_tool_categories="status_pages")

        enabled_cats = VALID_CATEGORIES - {"status_pages"}
        expected_read = self._count_tools_in_categories(enabled_cats, "read")
        expected_write = self._count_tools_in_categories(enabled_cats, "write")
        self.assertEqual(mock_mcp.add_tool.call_count, expected_read + expected_write)

    @patch("pagerduty_mcp.server.FastMCP")
    def test_multiple_disabled_categories(self, mock_fastmcp_class, _mock_strategy):
        """Test that disabling multiple categories excludes all their tools."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        mock_mcp.run = MagicMock()

        run(enable_write_tools=False, disabled_tool_categories="status_pages,change_events,alert_grouping")

        enabled_cats = VALID_CATEGORIES - {"status_pages", "change_events", "alert_grouping"}
        expected_read = self._count_tools_in_categories(enabled_cats, "read")
        self.assertEqual(mock_mcp.add_tool.call_count, expected_read)

    @patch("pagerduty_mcp.server.FastMCP")
    def test_disabled_category_write_tools_not_registered(self, mock_fastmcp_class, _mock_strategy):
        """Test that write tools of disabled categories are not registered even with write enabled."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        mock_mcp.run = MagicMock()

        run(enable_write_tools=True, disabled_tool_categories="teams")

        # Collect all tool functions passed to add_tool
        registered_tools = [call.args[0] for call in mock_mcp.add_tool.call_args_list]

        # None of the teams tools should be registered
        for tool in TOOL_CATEGORIES["teams"]["read"] + TOOL_CATEGORIES["teams"]["write"]:
            self.assertNotIn(tool, registered_tools)

    @patch("pagerduty_mcp.server.FastMCP")
    def test_disabled_write_only_category_still_excludes_reads(self, mock_fastmcp_class, _mock_strategy):
        """Test disabling a category with no write tools still excludes its reads."""
        mock_mcp = MagicMock()
        mock_fastmcp_class.return_value = mock_mcp
        mock_mcp.run = MagicMock()

        # oncalls has only read tools
        run(enable_write_tools=False, disabled_tool_categories="oncalls")

        registered_tools = [call.args[0] for call in mock_mcp.add_tool.call_args_list]
        for tool in TOOL_CATEGORIES["oncalls"]["read"]:
            self.assertNotIn(tool, registered_tools)


if __name__ == "__main__":
    unittest.main()
