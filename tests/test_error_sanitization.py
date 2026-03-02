"""Tests for error message sanitization (Issue #3 - Internal URL leakage)."""

import unittest
from unittest.mock import MagicMock, patch

from pagerduty.errors import Error as PDError
from pagerduty.errors import HttpError as PDHttpError

from pagerduty_mcp.context.application_context_strategy import PagerdutyMCPClient


class TestErrorSanitization(unittest.TestCase):
    """Test that internal URLs are stripped from error messages."""

    def test_sanitize_kubernetes_url_get(self):
        """Internal Kubernetes URL should be replaced with 'PagerDuty API:'."""
        msg = "GET http://bff-public-api.bff-public-api.svc.cluster.local:80/api/v1/services: 404 Not Found"
        result = PagerdutyMCPClient._sanitize_error_message(msg)
        self.assertNotIn("svc.cluster.local", result)
        self.assertIn("GET PagerDuty API:", result)
        self.assertIn("404 Not Found", result)

    def test_sanitize_kubernetes_url_post(self):
        """POST with internal URL should also be sanitized."""
        msg = "POST https://internal-service.namespace.svc.cluster.local:443/incidents: 400 Bad Request"
        result = PagerdutyMCPClient._sanitize_error_message(msg)
        self.assertNotIn("internal-service", result)
        self.assertIn("POST PagerDuty API:", result)
        self.assertIn("400 Bad Request", result)

    def test_sanitize_preserves_public_api_url(self):
        """Public PagerDuty API URLs should also be sanitized (we strip all URLs)."""
        msg = "GET https://api.pagerduty.com:443/services/PXXXXXX: 404 Not Found"
        result = PagerdutyMCPClient._sanitize_error_message(msg)
        self.assertIn("GET PagerDuty API:", result)

    def test_sanitize_no_url_passthrough(self):
        """Messages without URLs should pass through unchanged."""
        msg = "Something went wrong"
        result = PagerdutyMCPClient._sanitize_error_message(msg)
        self.assertEqual(result, msg)

    def test_sanitize_delete_method(self):
        """DELETE method URLs should be sanitized."""
        msg = "DELETE http://bff-public-api.bff-public-api.svc.cluster.local:80/teams/TEAM123: 404"
        result = PagerdutyMCPClient._sanitize_error_message(msg)
        self.assertNotIn("svc.cluster.local", result)
        self.assertIn("DELETE PagerDuty API:", result)

    def test_sanitize_put_method(self):
        """PUT method URLs should be sanitized."""
        msg = "PUT http://bff-public-api.bff-public-api.svc.cluster.local:80/services/SVC123: 400"
        result = PagerdutyMCPClient._sanitize_error_message(msg)
        self.assertNotIn("svc.cluster.local", result)
        self.assertIn("PUT PagerDuty API:", result)

    @patch.object(PagerdutyMCPClient, "__init__", lambda self, *a, **kw: None)
    def test_rget_sanitizes_http_error(self):
        """Rget should catch PDHttpError and re-raise with sanitized message."""
        client = PagerdutyMCPClient.__new__(PagerdutyMCPClient)
        mock_response = MagicMock()
        original_msg = "GET http://bff-public-api.svc.cluster.local:80/services: 404 Not Found"

        with patch.object(
            PagerdutyMCPClient.__bases__[0], "rget", side_effect=PDHttpError(original_msg, mock_response)
        ):
            with self.assertRaises(PDHttpError) as ctx:
                client.rget("/services")

            self.assertNotIn("svc.cluster.local", str(ctx.exception))
            self.assertIn("GET PagerDuty API:", str(ctx.exception))

    @patch.object(PagerdutyMCPClient, "__init__", lambda self, *a, **kw: None)
    def test_rpost_sanitizes_http_error(self):
        """Rpost should catch PDHttpError and re-raise with sanitized message."""
        client = PagerdutyMCPClient.__new__(PagerdutyMCPClient)
        mock_response = MagicMock()
        original_msg = "POST http://bff-public-api.svc.cluster.local:80/incidents: 400 Bad Request"

        with patch.object(
            PagerdutyMCPClient.__bases__[0], "rpost", side_effect=PDHttpError(original_msg, mock_response)
        ):
            with self.assertRaises(PDHttpError) as ctx:
                client.rpost("/incidents", json={})

            self.assertNotIn("svc.cluster.local", str(ctx.exception))
            self.assertIn("POST PagerDuty API:", str(ctx.exception))

    @patch.object(PagerdutyMCPClient, "__init__", lambda self, *a, **kw: None)
    def test_rdelete_sanitizes_pd_error(self):
        """Rdelete should catch PDError and re-raise with sanitized message."""
        client = PagerdutyMCPClient.__new__(PagerdutyMCPClient)
        original_msg = "DELETE http://bff-public-api.svc.cluster.local:80/teams/T123: connection error"

        with patch.object(
            PagerdutyMCPClient.__bases__[0], "rdelete", side_effect=PDError(original_msg)
        ):
            with self.assertRaises(PDError) as ctx:
                client.rdelete("/teams/T123")

            self.assertNotIn("svc.cluster.local", str(ctx.exception))
            self.assertIn("DELETE PagerDuty API:", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
