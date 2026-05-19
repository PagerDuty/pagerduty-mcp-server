import os
import unittest
from unittest.mock import patch

import pagerduty_mcp.context.application_context_strategy as m


class TestApplicationContextStrategy(unittest.TestCase):

    @patch.dict(os.environ, {"PAGERDUTY_USER_API_KEY": "test-key"}, clear=True)
    @patch("pagerduty_mcp.context.application_context_strategy.PagerdutyMCPClient")
    def test_default_auth_type_is_token(self, mock_cls):
        m.create_pd_client()
        mock_cls.assert_called_once()
        _, kwargs = mock_cls.call_args
        self.assertEqual(kwargs.get("auth_type", "token"), "token")

    @patch.dict(os.environ, {"PAGERDUTY_USER_API_KEY": "test-key", "PAGERDUTY_AUTH_TYPE": "token"}, clear=True)
    @patch("pagerduty_mcp.context.application_context_strategy.PagerdutyMCPClient")
    def test_explicit_token_auth_type(self, mock_cls):
        m.create_pd_client()
        mock_cls.assert_called_once()
        _, kwargs = mock_cls.call_args
        self.assertEqual(kwargs.get("auth_type"), "token")

    @patch.dict(os.environ, {"PAGERDUTY_USER_API_KEY": "test-key", "PAGERDUTY_AUTH_TYPE": "oauth2"}, clear=True)
    @patch("pagerduty_mcp.context.application_context_strategy.PagerdutyMCPClient")
    def test_oauth2_auth_type(self, mock_cls):
        m.create_pd_client()
        mock_cls.assert_called_once()
        _, kwargs = mock_cls.call_args
        self.assertEqual(kwargs.get("auth_type"), "oauth2")

    @patch.dict(os.environ, {"PAGERDUTY_USER_API_KEY": "test-key", "PAGERDUTY_AUTH_TYPE": "invalid"}, clear=True)
    def test_invalid_auth_type_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            m.create_pd_client()
        self.assertIn("PAGERDUTY_AUTH_TYPE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
