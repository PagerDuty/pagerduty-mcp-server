import json
import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.references import PriorityReference
from pagerduty_mcp.tools.priorities import list_priorities


class TestPrioritiesTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client = MagicMock()

    def setUp(self):
        self.mock_client.reset_mock()
        self.mock_client.side_effect = None

    @patch("pagerduty_mcp.tools.priorities.paginate")
    @patch("pagerduty_mcp.tools.priorities.get_client")
    def test_list_priorities_returns_json_string(self, mock_get_client, mock_paginate):
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [
            {"id": "P1", "summary": "Critical"},
            {"id": "P2", "summary": "High"},
        ]

        result = list_priorities()

        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertIn("response", parsed)
        self.assertEqual(len(parsed["response"]), 2)
        self.assertEqual(parsed["response"][0]["id"], "P1")
        self.assertEqual(parsed["response"][0]["summary"], "Critical")
        self.assertEqual(parsed["response"][1]["id"], "P2")
        self.assertEqual(parsed["response"][1]["summary"], "High")

    @patch("pagerduty_mcp.tools.priorities.paginate")
    @patch("pagerduty_mcp.tools.priorities.get_client")
    def test_list_priorities_empty_response(self, mock_get_client, mock_paginate):
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        result = list_priorities()

        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertEqual(parsed["response"], [])

    @patch("pagerduty_mcp.tools.priorities.paginate")
    @patch("pagerduty_mcp.tools.priorities.get_client")
    def test_list_priorities_calls_paginate_correctly(self, mock_get_client, mock_paginate):
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        list_priorities()

        mock_paginate.assert_called_once_with(
            client=self.mock_client,
            entity="priorities",
            params={},
            maximum_records=100,
        )

    @patch("pagerduty_mcp.tools.priorities.paginate")
    @patch("pagerduty_mcp.tools.priorities.get_client")
    def test_list_priorities_paginate_error(self, mock_get_client, mock_paginate):
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("Pagination Error")

        with self.assertRaises(Exception) as ctx:
            list_priorities()

        self.assertEqual(str(ctx.exception), "Pagination Error")

    def test_priority_reference_model(self):
        priority = PriorityReference(id="P1", summary="P1 name")

        self.assertEqual(priority.type, "priority_reference")
        self.assertEqual(priority.id, "P1")
        self.assertEqual(priority.summary, "P1 name")


if __name__ == "__main__":
    unittest.main()
