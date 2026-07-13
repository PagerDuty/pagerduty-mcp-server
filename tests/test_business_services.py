import json
import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.tools.business_services import (
    get_business_service_dependencies,
    list_business_services,
)


class TestBusinessServicesTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client = MagicMock()

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.side_effect = None
        self.mock_client.get.side_effect = None

    # --- list_business_services ---

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_returns_json_string(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "business_services": [
                {"id": "BS1", "name": "Checkout"},
                {"id": "BS2", "name": "Auth"},
            ]
        }
        self.mock_client.get.return_value = mock_response

        result = list_business_services()

        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertIn("response", parsed)
        self.assertEqual(len(parsed["response"]), 2)
        self.assertEqual(parsed["response"][0]["id"], "BS1")
        self.assertEqual(parsed["response"][1]["id"], "BS2")

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_empty(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"business_services": []}
        self.mock_client.get.return_value = mock_response

        result = list_business_services()

        parsed = json.loads(result)
        self.assertEqual(parsed, {"response": []})

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_calls_get_correctly(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"business_services": []}
        self.mock_client.get.return_value = mock_response

        list_business_services()

        self.mock_client.get.assert_called_once_with(
            "/business_services", params={"limit": 100}
        )

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_client_error(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as ctx:
            list_business_services()

        self.assertEqual(str(ctx.exception), "API Error")

    # --- get_business_service_dependencies ---

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_business_service_dependencies_returns_relationships(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "relationships": [{"id": "REL1"}, {"id": "REL2"}]
        }
        self.mock_client.get.return_value = mock_response

        result = get_business_service_dependencies("BS123")

        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertIn("relationships", parsed)
        self.assertEqual(len(parsed["relationships"]), 2)
        self.assertEqual(parsed["relationships"][0]["id"], "REL1")
        self.assertEqual(parsed["relationships"][1]["id"], "REL2")

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_business_service_dependencies_empty(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        self.mock_client.get.return_value = mock_response

        result = get_business_service_dependencies("BS123")

        parsed = json.loads(result)
        self.assertEqual(parsed, {"relationships": []})

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_business_service_dependencies_calls_get_correctly(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"relationships": []}
        self.mock_client.get.return_value = mock_response

        get_business_service_dependencies("BS123")

        self.mock_client.get.assert_called_once_with(
            "/service_dependencies/business_services/BS123"
        )

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_business_service_dependencies_client_error(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.side_effect = Exception("Dependency Error")

        with self.assertRaises(Exception) as ctx:
            get_business_service_dependencies("BS123")

        self.assertEqual(str(ctx.exception), "Dependency Error")


if __name__ == "__main__":
    unittest.main()
