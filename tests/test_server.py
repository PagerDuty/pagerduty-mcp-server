import unittest
import unittest.mock
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from pagerduty_mcp.server import Transport, app
from pagerduty_mcp.tools import read_tools, write_tools


class TestTransportEnum(unittest.TestCase):
    """Test cases for the Transport enum."""

    def test_transport_values(self):
        self.assertEqual(Transport.stdio.value, "stdio")
        self.assertEqual(Transport.sse.value, "sse")
        self.assertEqual(Transport.streamable_http.value, "streamable-http")

    def test_transport_is_str(self):
        self.assertIsInstance(Transport.stdio, str)
        self.assertIsInstance(Transport.streamable_http, str)

    def test_transport_default_is_stdio(self):
        self.assertEqual(Transport.stdio, Transport("stdio"))


class TestServerRun(unittest.TestCase):
    """Test cases for the run() CLI command."""

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, args=None, env=None):
        """Helper: invoke app with mocked FastMCP and ApplicationContextStrategy."""
        args = args or []
        with patch("pagerduty_mcp.server.FastMCP") as mock_fastmcp, \
             patch("pagerduty_mcp.server.ApplicationContextStrategy"), \
             patch("pagerduty_mcp.server.ContextResolver"):
            mock_mcp = MagicMock()
            mock_fastmcp.return_value = mock_mcp
            result = self.runner.invoke(app, args, env=env)
            return result, mock_fastmcp, mock_mcp

    def test_default_transport_is_stdio(self):
        result, _, mock_mcp = self._invoke()
        self.assertEqual(result.exit_code, 0, result.output)
        mock_mcp.run.assert_called_once_with(transport="stdio")

    def test_streamable_http_transport(self):
        result, _, mock_mcp = self._invoke(["--transport", "streamable-http"])
        self.assertEqual(result.exit_code, 0, result.output)
        mock_mcp.run.assert_called_once_with(transport="streamable-http")

    def test_sse_transport(self):
        result, _, mock_mcp = self._invoke(["--transport", "sse"])
        self.assertEqual(result.exit_code, 0, result.output)
        mock_mcp.run.assert_called_once_with(transport="sse")

    def test_default_host_and_port_for_http_transport(self):
        result, mock_fastmcp, _ = self._invoke(["--transport", "streamable-http"])
        self.assertEqual(result.exit_code, 0, result.output)
        mock_fastmcp.assert_called_once_with(
            "PagerDuty MCP Server",
            instructions=unittest.mock.ANY,
            host="127.0.0.1",
            port=8000,
            transport_security=unittest.mock.ANY,
        )

    def test_stdio_does_not_pass_host_or_port_to_fastmcp(self):
        result, mock_fastmcp, _ = self._invoke()
        self.assertEqual(result.exit_code, 0, result.output)
        mock_fastmcp.assert_called_once_with(
            "PagerDuty MCP Server",
            instructions=unittest.mock.ANY,
        )

    def test_custom_host_and_port_via_cli(self):
        result, mock_fastmcp, _ = self._invoke(
            ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000"]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        mock_fastmcp.assert_called_once_with(
            "PagerDuty MCP Server",
            instructions=unittest.mock.ANY,
            host="0.0.0.0",
            port=9000,
        )

    def test_host_from_env_var(self):
        result, mock_fastmcp, _ = self._invoke(
            ["--transport", "streamable-http"], env={"MCP_HOST": "0.0.0.0"}
        )
        self.assertEqual(result.exit_code, 0, result.output)
        mock_fastmcp.assert_called_once_with(
            "PagerDuty MCP Server",
            instructions=unittest.mock.ANY,
            host="0.0.0.0",
            port=8000,
        )

    def test_port_from_env_var(self):
        result, mock_fastmcp, _ = self._invoke(
            ["--transport", "streamable-http"], env={"MCP_PORT": "9000"}
        )
        self.assertEqual(result.exit_code, 0, result.output)
        mock_fastmcp.assert_called_once_with(
            "PagerDuty MCP Server",
            instructions=unittest.mock.ANY,
            host="127.0.0.1",
            port=9000,
            transport_security=unittest.mock.ANY,
        )

    def test_cli_flag_overrides_env_var(self):
        result, mock_fastmcp, _ = self._invoke(
            ["--transport", "streamable-http", "--host", "192.168.1.1"],
            env={"MCP_HOST": "0.0.0.0"},
        )
        self.assertEqual(result.exit_code, 0, result.output)
        mock_fastmcp.assert_called_once_with(
            "PagerDuty MCP Server",
            instructions=unittest.mock.ANY,
            host="192.168.1.1",
            port=8000,
        )

    def test_dns_rebinding_protection_enabled_for_http(self):
        from mcp.server.transport_security import TransportSecuritySettings
        result, mock_fastmcp, _ = self._invoke(["--transport", "streamable-http"])
        self.assertEqual(result.exit_code, 0, result.output)
        call_kwargs = mock_fastmcp.call_args.kwargs
        ts = call_kwargs.get("transport_security")
        self.assertIsInstance(ts, TransportSecuritySettings)
        self.assertTrue(ts.enable_dns_rebinding_protection)

    def test_dns_rebinding_loopback_restricts_allowed_hosts(self):
        from mcp.server.transport_security import TransportSecuritySettings
        result, mock_fastmcp, _ = self._invoke(
            ["--transport", "streamable-http", "--host", "127.0.0.1", "--port", "9000"]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        ts = mock_fastmcp.call_args.kwargs.get("transport_security")
        self.assertIsInstance(ts, TransportSecuritySettings)
        self.assertIn("127.0.0.1:9000", ts.allowed_hosts)

    def test_dns_rebinding_wildcard_bind_omits_transport_security(self):
        result, mock_fastmcp, _ = self._invoke(
            ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000"]
        )
        self.assertEqual(result.exit_code, 0, result.output)
        call_kwargs = mock_fastmcp.call_args.kwargs
        self.assertNotIn("transport_security", call_kwargs)

    def test_invalid_transport_fails(self):
        result, _, _ = self._invoke(["--transport", "invalid"])
        self.assertNotEqual(result.exit_code, 0)

    def test_port_zero_fails_for_http_transport(self):
        result, _, _ = self._invoke(["--transport", "streamable-http", "--port", "0"])
        self.assertNotEqual(result.exit_code, 0)

    def test_port_out_of_range_fails_for_http_transport(self):
        result, _, _ = self._invoke(["--transport", "streamable-http", "--port", "99999"])
        self.assertNotEqual(result.exit_code, 0)

    def test_port_out_of_range_ignored_for_stdio(self):
        result, _, _ = self._invoke(["--port", "99999"])
        self.assertEqual(result.exit_code, 0, result.output)

    def test_host_with_control_characters_fails(self):
        for bad_host in ["bad\nhost", "bad\rhost", "bad\x00host", "bad\thost"]:
            with self.subTest(host=bad_host):
                result, _, _ = self._invoke(["--transport", "streamable-http", "--host", bad_host])
                self.assertNotEqual(result.exit_code, 0, f"Expected failure for host={bad_host!r}")

    def test_no_warning_for_loopback_variants(self):
        for loopback in ["127.0.0.1", "::1", "localhost", "LOCALHOST", "  127.0.0.1  ", "127.0.0.2"]:
            with self.subTest(host=loopback):
                result, _, _ = self._invoke(["--transport", "streamable-http", "--host", loopback])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertNotIn("no built-in authentication", result.output)

    def test_warning_emitted_when_http_env_vars_set_in_stdio_mode(self):
        with self.assertLogs("pagerduty_mcp.server", level="WARNING") as cm:
            result, _, _ = self._invoke(env={"MCP_HOST": "0.0.0.0"})
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(any("no effect" in m for m in cm.output))

    def test_warning_emitted_for_non_loopback_http(self):
        with self.assertLogs("pagerduty_mcp.server", level="WARNING") as cm:
            result, _, _ = self._invoke(["--transport", "streamable-http", "--host", "0.0.0.0"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(any("no built-in authentication" in m for m in cm.output))

    def test_privileged_port_warning(self):
        with self.assertLogs("pagerduty_mcp.server", level="WARNING") as cm:
            result, _, _ = self._invoke(["--transport", "streamable-http", "--port", "80"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(any("privileged port" in m for m in cm.output))

    def test_write_tools_not_registered_by_default(self):
        result, _, mock_mcp = self._invoke()
        self.assertEqual(result.exit_code, 0, result.output)
        # Only read_tools should be registered — count must equal len(read_tools)
        self.assertEqual(mock_mcp.add_tool.call_count, len(read_tools))

    def test_write_tools_registered_when_flag_set(self):
        result, _, mock_mcp = self._invoke(["--enable-write-tools"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_mcp.add_tool.call_count, len(read_tools) + len(write_tools))


if __name__ == "__main__":
    unittest.main()
