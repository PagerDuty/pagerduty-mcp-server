import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT, Relationship
from pagerduty_mcp.models.business_services import (
    BusinessService,
    BusinessServiceDependencyList,
    BusinessServiceQuery,
)
from pagerduty_mcp.tools.business_services import (
    get_business_service_dependencies,
    list_business_services,
)


class TestBusinessServiceTools(unittest.TestCase):
    """Test cases for business service tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data reused across all test methods."""
        cls.sample_business_service = {
            "id": "BS123",
            "name": "Payment Processing",
            "description": "Handles all payment transactions",
            "point_of_contact": "payments-team@example.com",
            "team": {"id": "TEAM1", "summary": "Payments Team", "type": "team_reference"},
            "type": "business_service",
        }

        cls.sample_business_services_list = [
            {
                "id": "BS123",
                "name": "Payment Processing",
                "description": "Handles all payment transactions",
                "point_of_contact": None,
                "team": {"id": "TEAM1", "summary": "Payments Team", "type": "team_reference"},
                "type": "business_service",
            },
            {
                "id": "BS456",
                "name": "Customer Portal",
                "description": "Customer-facing web portal",
                "point_of_contact": None,
                "team": None,
                "type": "business_service",
            },
        ]

        cls.sample_relationships_response = {
            "relationships": [
                {
                    "id": "DEP001",
                    "type": "service_dependency",
                    "supporting_service": {
                        "id": "BS123",
                        "type": "business_service_reference",
                    },
                    "dependent_service": {
                        "id": "BS789",
                        "type": "business_service_reference",
                    },
                },
                {
                    "id": "DEP002",
                    "type": "service_dependency",
                    "supporting_service": {
                        "id": "SVC001",
                        "type": "technical_service_reference",
                    },
                    "dependent_service": {
                        "id": "BS123",
                        "type": "business_service_reference",
                    },
                },
            ]
        }

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        self.mock_client.get.side_effect = None

    # -------------------------------------------------------------------------
    # list_business_services
    # -------------------------------------------------------------------------

    @patch("pagerduty_mcp.tools.business_services.paginate")
    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_default(self, mock_get_client, mock_paginate):
        """Test listing business services with default parameters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_business_services_list

        query = BusinessServiceQuery()
        result = list_business_services(query)

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="business_services", params=query.to_params()
        )
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], BusinessService)
        self.assertEqual(result.response[0].id, "BS123")
        self.assertEqual(result.response[0].name, "Payment Processing")
        self.assertEqual(result.response[1].id, "BS456")

    @patch("pagerduty_mcp.tools.business_services.paginate")
    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing business services with a custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_business_services_list

        query = BusinessServiceQuery(limit=50)
        list_business_services(query)

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="business_services", params={"limit": 50}
        )

    @patch("pagerduty_mcp.tools.business_services.paginate")
    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_empty_response(self, mock_get_client, mock_paginate):
        """Test listing business services when no services exist."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        result = list_business_services(BusinessServiceQuery())

        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.business_services.paginate")
    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_list_business_services_paginate_error(self, mock_get_client, mock_paginate):
        """Test list_business_services propagates paginate exceptions."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as ctx:
            list_business_services(BusinessServiceQuery())

        self.assertEqual(str(ctx.exception), "API Error")

    # -------------------------------------------------------------------------
    # get_business_service_dependencies
    # -------------------------------------------------------------------------

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_dependencies_returns_relationships(self, mock_get_client):
        """Test fetching dependencies returns all relationships."""
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_relationships_response
        self.mock_client.get.return_value = mock_response

        result = get_business_service_dependencies("BS123")

        self.mock_client.get.assert_called_once_with(
            "/service_dependencies/business_services/BS123"
        )
        self.assertIsInstance(result, BusinessServiceDependencyList)
        self.assertEqual(len(result.relationships), 2)
        self.assertIsInstance(result.relationships[0], Relationship)
        self.assertEqual(result.relationships[0].id, "DEP001")
        self.assertIsNotNone(result.relationships[0].supporting_service)
        self.assertEqual(result.relationships[0].supporting_service.get("id"), "BS123")  # type: ignore[union-attr]
        self.assertIsNotNone(result.relationships[1].dependent_service)
        self.assertEqual(result.relationships[1].dependent_service.get("id"), "BS123")  # type: ignore[union-attr]

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_dependencies_empty(self, mock_get_client):
        """Test fetching dependencies for a service with no relationships."""
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"relationships": []}
        self.mock_client.get.return_value = mock_response

        result = get_business_service_dependencies("BS999")

        self.assertIsInstance(result, BusinessServiceDependencyList)
        self.assertEqual(len(result.relationships), 0)

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_dependencies_uses_correct_endpoint(self, mock_get_client):
        """Test that the correct API endpoint is called."""
        mock_get_client.return_value = self.mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"relationships": []}
        self.mock_client.get.return_value = mock_response

        get_business_service_dependencies("BSABC")

        self.mock_client.get.assert_called_once_with(
            "/service_dependencies/business_services/BSABC"
        )

    @patch("pagerduty_mcp.tools.business_services.get_client")
    def test_get_dependencies_client_error(self, mock_get_client):
        """Test get_business_service_dependencies propagates client exceptions."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.get.side_effect = Exception("Network Error")

        with self.assertRaises(Exception) as ctx:
            get_business_service_dependencies("BS123")

        self.assertEqual(str(ctx.exception), "Network Error")

    # -------------------------------------------------------------------------
    # Model validation
    # -------------------------------------------------------------------------

    def test_business_service_computed_type(self):
        """Test BusinessService computed type property always returns 'business_service'."""
        service = BusinessService(id="BS1", name="My Service")
        self.assertEqual(service.type, "business_service")

    def test_business_service_optional_fields(self):
        """Test BusinessService with only required fields."""
        service = BusinessService()
        self.assertIsNone(service.id)
        self.assertIsNone(service.name)
        self.assertIsNone(service.team)
        self.assertEqual(service.type, "business_service")

    def test_business_service_query_default_params(self):
        """Test BusinessServiceQuery.to_params() with defaults."""
        query = BusinessServiceQuery()
        self.assertEqual(query.to_params(), {"limit": DEFAULT_PAGINATION_LIMIT})

    def test_business_service_query_custom_limit(self):
        """Test BusinessServiceQuery.to_params() with a custom limit."""
        query = BusinessServiceQuery(limit=50)
        self.assertEqual(query.to_params(), {"limit": 50})

    def test_business_service_query_limit_bounds(self):
        """Test BusinessServiceQuery validates limit within allowed bounds."""
        self.assertEqual(BusinessServiceQuery(limit=1).limit, 1)
        self.assertEqual(BusinessServiceQuery(limit=MAXIMUM_PAGINATION_LIMIT).limit, MAXIMUM_PAGINATION_LIMIT)

    def test_relationship_model_fields(self):
        """Test Relationship model accepts all expected fields."""
        rel = Relationship(
            id="DEP001",
            type="service_dependency",
            supporting_service={"id": "SVC1", "type": "technical_service_reference"},
            dependent_service={"id": "BS1", "type": "business_service_reference"},
        )
        self.assertEqual(rel.id, "DEP001")
        self.assertIsNotNone(rel.supporting_service)
        self.assertIsNotNone(rel.dependent_service)
        self.assertEqual(rel.supporting_service.get("id"), "SVC1")  # type: ignore[union-attr]
        self.assertEqual(rel.dependent_service.get("id"), "BS1")  # type: ignore[union-attr]

    def test_relationship_model_optional_fields(self):
        """Test Relationship model with no fields set."""
        rel = Relationship()
        self.assertIsNone(rel.id)
        self.assertIsNone(rel.supporting_service)
        self.assertIsNone(rel.dependent_service)


if __name__ == "__main__":
    unittest.main()
