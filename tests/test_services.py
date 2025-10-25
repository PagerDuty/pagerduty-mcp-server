import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.escalation_policies import EscalationPolicyReference
from pagerduty_mcp.models.references import TeamReference
from pagerduty_mcp.models.services import Service, ServiceCreate, ServiceQuery
from pagerduty_mcp.tools.services import (
    create_service,
    get_service,
    list_services,
    update_service,
)


class TestServiceTools(unittest.TestCase):
    """Test cases for service tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_escalation_policy = {
            "id": "EP123",
            "summary": "Default Escalation Policy",
            "type": "escalation_policy_reference",
        }

        cls.sample_service_response = {
            "id": "SVC123",
            "name": "Web Application Service",
            "description": "Main web application service",
            "escalation_policy": cls.sample_escalation_policy,
            "teams": [
                {"id": "TEAM1", "summary": "Engineering Team", "type": "team_reference"},
                {"id": "TEAM2", "summary": "DevOps Team", "type": "team_reference"},
            ],
        }

        cls.sample_services_list_response = [
            {
                "id": "SVC123",
                "name": "Web Application Service",
                "description": "Main web application service",
                "escalation_policy": cls.sample_escalation_policy,
                "teams": [{"id": "TEAM1", "summary": "Engineering Team", "type": "team_reference"}],
            },
            {
                "id": "SVC456",
                "name": "Database Service",
                "description": "Database monitoring service",
                "escalation_policy": cls.sample_escalation_policy,
                "teams": [{"id": "TEAM2", "summary": "DevOps Team", "type": "team_reference"}],
            },
        ]

        cls.sample_service_create_data = {
            "service": {
                "name": "New API Service",
                "description": "RESTful API service",
                "escalation_policy": cls.sample_escalation_policy,
                "teams": [{"id": "TEAM1", "summary": "Engineering Team", "type": "team_reference"}],
            }
        }

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None
        self.mock_client.rput.side_effect = None

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_no_filters(self, mock_get_client, mock_paginate):
        """Test listing services without any filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_services_list_response

        query = ServiceQuery()
        result = list_services(query)

        # Verify paginate call
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="services", params=query.to_params(), maximum_records=query.limit or 1000)

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], Service)
        self.assertIsInstance(result.response[1], Service)
        self.assertEqual(result.response[0].id, "SVC123")
        self.assertEqual(result.response[1].id, "SVC456")
        self.assertEqual(result.response[0].name, "Web Application Service")
        self.assertEqual(result.response[1].name, "Database Service")

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_with_query_filter(self, mock_get_client, mock_paginate):
        """Test listing services with query filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_services_list_response[0]]

        query = ServiceQuery(query="Web")
        result = list_services(query)

        # Verify paginate call
        expected_params = {"query": "Web", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="services", params=expected_params, maximum_records=expected_params.get("limit") or 1000)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Web Application Service")

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_with_teams_filter(self, mock_get_client, mock_paginate):
        """Test listing services with teams filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_services_list_response[1]]

        query = ServiceQuery(teams_ids=["TEAM2"])
        result = list_services(query)

        # Verify paginate call
        expected_params = {"teams_ids[]": ["TEAM2"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="services", params=expected_params, maximum_records=expected_params.get("limit") or 1000)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Database Service")

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_with_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing services with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_services_list_response

        query = ServiceQuery(limit=50)
        result = list_services(query)

        # Verify paginate call
        expected_params = {"limit": 50}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="services", params=expected_params, maximum_records=expected_params.get("limit") or 1000)

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_with_all_filters(self, mock_get_client, mock_paginate):
        """Test listing services with all filters applied."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_services_list_response[0]]

        query = ServiceQuery(query="Web", teams_ids=["TEAM1"], limit=10)
        result = list_services(query)

        # Verify paginate call
        expected_params = {"query": "Web", "teams_ids[]": ["TEAM1"], "limit": 10}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="services", params=expected_params, maximum_records=expected_params.get("limit") or 1000)

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Web Application Service")

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_empty_response(self, mock_get_client, mock_paginate):
        """Test listing services when paginate returns empty list."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        query = ServiceQuery(query="NonExistentService")
        result = list_services(query)

        # Verify paginate call
        expected_params = {"query": "NonExistentService", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="services", params=expected_params, maximum_records=expected_params.get("limit") or 1000)

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.services.paginate")
    @patch("pagerduty_mcp.tools.services.get_client")
    def test_list_services_paginate_error(self, mock_get_client, mock_paginate):
        """Test list_services when paginate raises an exception."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("Pagination Error")

        query = ServiceQuery()

        with self.assertRaises(Exception) as context:
            list_services(query)

        self.assertEqual(str(context.exception), "Pagination Error")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_get_service_success(self, mock_get_client):
        """Test successful retrieval of a specific service."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_service_response

        result = get_service("SVC123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/services/SVC123")

        # Verify result
        self.assertIsInstance(result, Service)
        self.assertEqual(result.id, "SVC123")
        self.assertEqual(result.name, "Web Application Service")
        self.assertEqual(result.description, "Main web application service")
        self.assertIsInstance(result.escalation_policy, EscalationPolicyReference)
        self.assertEqual(result.escalation_policy.id, "EP123")
        self.assertEqual(len(result.teams), 2)
        self.assertIsInstance(result.teams[0], TeamReference)
        self.assertEqual(result.teams[0].id, "TEAM1")
        self.assertEqual(result.teams[1].id, "TEAM2")
        self.assertEqual(result.type, "service")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_get_service_client_error(self, mock_get_client):
        """Test get_service when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_service("SVC123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/services/SVC123")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_create_service_success_wrapped_response(self, mock_get_client):
        """Test successful service creation with wrapped response."""
        mock_get_client.return_value = self.mock_client
        # API response with service wrapped in 'service' key
        wrapped_response = {"service": self.sample_service_response}
        self.mock_client.rpost.return_value = wrapped_response

        # Create ServiceCreate instance
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Default Escalation Policy")
        teams = [TeamReference(id="TEAM1", summary="Engineering Team")]
        service_data = Service(
            name="New API Service", description="RESTful API service", escalation_policy=escalation_policy, teams=teams
        )
        service_create = ServiceCreate(service=service_data)

        result = create_service(service_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once_with("/services", json=service_create.model_dump())

        # Verify result
        self.assertIsInstance(result, Service)
        self.assertEqual(result.id, "SVC123")
        self.assertEqual(result.name, "Web Application Service")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_create_service_success_direct_response(self, mock_get_client):
        """Test successful service creation with direct response."""
        mock_get_client.return_value = self.mock_client
        # API response directly as service object
        self.mock_client.rpost.return_value = self.sample_service_response

        # Create ServiceCreate instance
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Default Escalation Policy")
        teams = [TeamReference(id="TEAM1", summary="Engineering Team")]
        service_data = Service(
            name="New API Service", description="RESTful API service", escalation_policy=escalation_policy, teams=teams
        )
        service_create = ServiceCreate(service=service_data)

        result = create_service(service_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once_with("/services", json=service_create.model_dump())

        # Verify result
        self.assertIsInstance(result, Service)
        self.assertEqual(result.id, "SVC123")
        self.assertEqual(result.name, "Web Application Service")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_create_service_client_error(self, mock_get_client):
        """Test create_service when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.side_effect = Exception("API Error")

        # Create ServiceCreate instance
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Default Escalation Policy")
        service_data = Service(
            name="New API Service", description="RESTful API service", escalation_policy=escalation_policy, teams=[]
        )
        service_create = ServiceCreate(service=service_data)

        with self.assertRaises(Exception) as context:
            create_service(service_create)

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_update_service_success_wrapped_response(self, mock_get_client):
        """Test successful service update with wrapped response."""
        mock_get_client.return_value = self.mock_client
        # API response with service wrapped in 'service' key
        updated_service = self.sample_service_response.copy()
        updated_service["name"] = "Updated Service Name"
        wrapped_response = {"service": updated_service}
        self.mock_client.rput.return_value = wrapped_response

        # Create ServiceCreate instance for update
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Default Escalation Policy")
        service_data = Service(
            name="Updated Service Name",
            description="Updated description",
            escalation_policy=escalation_policy,
            teams=[],
        )
        service_create = ServiceCreate(service=service_data)

        result = update_service("SVC123", service_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rput.assert_called_once_with("/services/SVC123", json=service_create.model_dump())

        # Verify result
        self.assertIsInstance(result, Service)
        self.assertEqual(result.id, "SVC123")
        self.assertEqual(result.name, "Updated Service Name")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_update_service_success_direct_response(self, mock_get_client):
        """Test successful service update with direct response."""
        mock_get_client.return_value = self.mock_client
        # API response directly as service object
        updated_service = self.sample_service_response.copy()
        updated_service["name"] = "Updated Service Name"
        self.mock_client.rput.return_value = updated_service

        # Create ServiceCreate instance for update
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Default Escalation Policy")
        service_data = Service(
            name="Updated Service Name",
            description="Updated description",
            escalation_policy=escalation_policy,
            teams=[],
        )
        service_create = ServiceCreate(service=service_data)

        result = update_service("SVC123", service_create)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rput.assert_called_once_with("/services/SVC123", json=service_create.model_dump())

        # Verify result
        self.assertIsInstance(result, Service)
        self.assertEqual(result.id, "SVC123")
        self.assertEqual(result.name, "Updated Service Name")

    @patch("pagerduty_mcp.tools.services.get_client")
    def test_update_service_client_error(self, mock_get_client):
        """Test update_service when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rput.side_effect = Exception("API Error")

        # Create ServiceCreate instance
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Default Escalation Policy")
        service_data = Service(
            name="Updated Service Name",
            description="Updated description",
            escalation_policy=escalation_policy,
            teams=[],
        )
        service_create = ServiceCreate(service=service_data)

        with self.assertRaises(Exception) as context:
            update_service("SVC123", service_create)

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()

    def test_service_query_to_params_all_fields(self):
        """Test ServiceQuery.to_params() with all fields set."""
        query = ServiceQuery(query="test service", teams_ids=["TEAM1", "TEAM2"], limit=25)

        params = query.to_params()

        expected_params = {"query": "test service", "teams_ids[]": ["TEAM1", "TEAM2"], "limit": 25}
        self.assertEqual(params, expected_params)

    def test_service_query_to_params_partial_fields(self):
        """Test ServiceQuery.to_params() with only some fields set."""
        query = ServiceQuery(query="test", limit=None)

        params = query.to_params()

        expected_params = {"query": "test"}
        self.assertEqual(params, expected_params)

    def test_service_query_to_params_empty(self):
        """Test ServiceQuery.to_params() with no fields set."""
        query = ServiceQuery()

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_service_query_validation_limit_bounds(self):
        """Test ServiceQuery limit validation within bounds."""
        # Test minimum limit
        query = ServiceQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = ServiceQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = ServiceQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)

    def test_service_model_computed_type(self):
        """Test Service model computed type property."""
        escalation_policy = EscalationPolicyReference(id="EP123", summary="Test Escalation Policy")
        service = Service(
            name="Test Service", description="Test Description", escalation_policy=escalation_policy, teams=[]
        )

        self.assertEqual(service.type, "service")


if __name__ == "__main__":
    unittest.main()
