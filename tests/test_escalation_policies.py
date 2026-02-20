import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT, MAXIMUM_PAGINATION_LIMIT
from pagerduty_mcp.models.escalation_policies import (
    EscalationPolicy,
    EscalationPolicyQuery,
    EscalationRule,
    EscalationTarget,
)
from pagerduty_mcp.tools.escalation_policies import (
    get_escalation_policy,
    list_escalation_policies,
)


class TestEscalationPolicyTools(unittest.TestCase):
    """Test cases for escalation policy tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_escalation_target = {
            "id": "USER123",
            "type": "user_reference",
            "summary": "John Doe - Senior Engineer",
        }

        cls.sample_escalation_rule = {
            "id": "RULE123",
            "escalation_delay_in_minutes": 30,
            "targets": [cls.sample_escalation_target],
            "escalation_rule_assignment_strategy": "assign_to_everyone",
        }

        cls.sample_escalation_policy_response = {
            "id": "EP123",
            "summary": "Engineering Escalation Policy",
            "name": "Engineering Team Escalation",
            "description": "Escalation policy for engineering incidents",
            "escalation_rules": [cls.sample_escalation_rule],
            "num_loops": 2,
            "on_call_handoff_notifications": "if_has_services",
            "self_url": "https://api.pagerduty.com/escalation_policies/EP123",
            "html_url": "https://mycompany.pagerduty.com/escalation_policies/EP123",
            "services": [
                {"id": "SVC123", "summary": "Backend Service", "type": "service_reference"},
            ],
            "teams": [
                {"id": "TEAM123", "summary": "Engineering Team", "type": "team_reference"},
            ],
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-06-01T12:00:00Z",
        }

        cls.sample_escalation_policies_list_response = [
            {
                "id": "EP123",
                "summary": "Engineering Escalation Policy",
                "name": "Engineering Team Escalation",
                "description": "Escalation policy for engineering incidents",
                "escalation_rules": [cls.sample_escalation_rule],
                "num_loops": 2,
            },
            {
                "id": "EP456",
                "summary": "DevOps Escalation Policy",
                "name": "DevOps Team Escalation",
                "description": "Escalation policy for infrastructure incidents",
                "escalation_rules": [
                    {
                        "id": "RULE456",
                        "escalation_delay_in_minutes": 15,
                        "targets": [
                            {
                                "id": "SCHED456",
                                "type": "schedule_reference",
                                "summary": "DevOps On-Call Schedule",
                            }
                        ],
                        "escalation_rule_assignment_strategy": "round_robin",
                    }
                ],
                "num_loops": 1,
            },
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_no_filters(self, mock_get_client, mock_paginate):
        """Test listing escalation policies without any filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_escalation_policies_list_response

        query = EscalationPolicyQuery()
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], EscalationPolicy)
        self.assertIsInstance(result.response[1], EscalationPolicy)
        self.assertEqual(result.response[0].id, "EP123")
        self.assertEqual(result.response[1].id, "EP456")
        self.assertEqual(result.response[0].name, "Engineering Team Escalation")
        self.assertEqual(result.response[1].name, "DevOps Team Escalation")

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_with_query_filter(self, mock_get_client, mock_paginate):
        """Test listing escalation policies with query filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_escalation_policies_list_response[0]]

        query = EscalationPolicyQuery(query="Engineering")
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"query": "Engineering", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].name, "Engineering Team Escalation")

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_with_user_filter(self, mock_get_client, mock_paginate):
        """Test listing escalation policies with user filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_escalation_policies_list_response

        query = EscalationPolicyQuery(user_ids=["USER123", "USER456"])
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"user_ids[]": ["USER123", "USER456"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_with_team_filter(self, mock_get_client, mock_paginate):
        """Test listing escalation policies with team filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_escalation_policies_list_response

        query = EscalationPolicyQuery(team_ids=["TEAM123"])
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"team_ids[]": ["TEAM123"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_with_include_filter(self, mock_get_client, mock_paginate):
        """Test listing escalation policies with include filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_escalation_policies_list_response

        query = EscalationPolicyQuery(include=["services", "teams"])
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"include[]": ["services", "teams"], "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_with_all_filters(self, mock_get_client, mock_paginate):
        """Test listing escalation policies with all filters applied."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_escalation_policies_list_response[0]]

        query = EscalationPolicyQuery(
            query="Engineering",
            user_ids=["USER123"],
            team_ids=["TEAM123"],
            include=["services"],
            limit=50,
        )
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {
            "query": "Engineering",
            "user_ids[]": ["USER123"],
            "team_ids[]": ["TEAM123"],
            "include[]": ["services"],
            "limit": 50,
        }
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 1)

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_with_custom_limit(self, mock_get_client, mock_paginate):
        """Test listing escalation policies with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_escalation_policies_list_response

        query = EscalationPolicyQuery(limit=50)
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"limit": 50}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_empty_response(self, mock_get_client, mock_paginate):
        """Test listing escalation policies when paginate returns empty list."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        query = EscalationPolicyQuery(query="NonExistentPolicy")
        result = list_escalation_policies(query)

        # Verify paginate call
        expected_params = {"query": "NonExistentPolicy", "limit": DEFAULT_PAGINATION_LIMIT}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="escalation_policies", params=expected_params
        )

        # Verify result
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.escalation_policies.paginate")
    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_list_escalation_policies_paginate_error(self, mock_get_client, mock_paginate):
        """Test list_escalation_policies when paginate raises an exception."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.side_effect = Exception("Pagination Error")

        query = EscalationPolicyQuery()

        with self.assertRaises(Exception) as context:
            list_escalation_policies(query)

        self.assertEqual(str(context.exception), "Pagination Error")

    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_get_escalation_policy_success(self, mock_get_client):
        """Test successful retrieval of a specific escalation policy."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_escalation_policy_response

        result = get_escalation_policy("EP123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/escalation_policies/EP123")

        # Verify result
        self.assertIsInstance(result, EscalationPolicy)
        self.assertEqual(result.id, "EP123")
        self.assertEqual(result.name, "Engineering Team Escalation")
        self.assertEqual(result.description, "Escalation policy for engineering incidents")
        self.assertEqual(result.summary, "Engineering Escalation Policy")
        self.assertEqual(result.num_loops, 2)
        self.assertEqual(result.on_call_handoff_notifications, "if_has_services")
        self.assertEqual(result.type, "escalation_policy")

        # Verify escalation rules
        self.assertEqual(len(result.escalation_rules), 1)
        rule = result.escalation_rules[0]
        self.assertEqual(rule.escalation_delay_in_minutes, 30)
        self.assertEqual(rule.escalation_rule_assignment_strategy, "assign_to_everyone")
        self.assertEqual(len(rule.targets), 1)

        target = rule.targets[0]
        self.assertEqual(target.id, "USER123")
        self.assertEqual(target.type, "user_reference")
        self.assertEqual(target.summary, "John Doe - Senior Engineer")

        # Verify references
        self.assertEqual(len(result.services), 1)
        self.assertEqual(result.services[0].id, "SVC123")
        self.assertEqual(len(result.teams), 1)
        self.assertEqual(result.teams[0].id, "TEAM123")

    @patch("pagerduty_mcp.tools.escalation_policies.get_client")
    def test_get_escalation_policy_client_error(self, mock_get_client):
        """Test get_escalation_policy when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            get_escalation_policy("EP123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/escalation_policies/EP123")

    def test_escalation_policy_query_to_params_all_fields(self):
        """Test EscalationPolicyQuery.to_params() with all fields set."""
        query = EscalationPolicyQuery(
            query="test policy",
            user_ids=["USER1", "USER2"],
            team_ids=["TEAM1", "TEAM2"],
            include=["services", "teams"],
            limit=25,
        )

        params = query.to_params()

        expected_params = {
            "query": "test policy",
            "user_ids[]": ["USER1", "USER2"],
            "team_ids[]": ["TEAM1", "TEAM2"],
            "include[]": ["services", "teams"],
            "limit": 25,
        }
        self.assertEqual(params, expected_params)

    def test_escalation_policy_query_to_params_partial_fields(self):
        """Test EscalationPolicyQuery.to_params() with only some fields set."""
        query = EscalationPolicyQuery(query="test", team_ids=["TEAM1"], limit=None)

        params = query.to_params()

        expected_params = {"query": "test", "team_ids[]": ["TEAM1"]}
        self.assertEqual(params, expected_params)

    def test_escalation_policy_query_to_params_empty(self):
        """Test EscalationPolicyQuery.to_params() with no fields set."""
        query = EscalationPolicyQuery()

        params = query.to_params()

        expected_params = {"limit": DEFAULT_PAGINATION_LIMIT}
        self.assertEqual(params, expected_params)

    def test_escalation_policy_query_validation_limit_bounds(self):
        """Test EscalationPolicyQuery limit validation within bounds."""
        # Test minimum limit
        query = EscalationPolicyQuery(limit=1)
        self.assertEqual(query.limit, 1)

        # Test maximum limit
        query = EscalationPolicyQuery(limit=MAXIMUM_PAGINATION_LIMIT)
        self.assertEqual(query.limit, MAXIMUM_PAGINATION_LIMIT)

        # Test default limit
        query = EscalationPolicyQuery()
        self.assertEqual(query.limit, DEFAULT_PAGINATION_LIMIT)

    def test_escalation_policy_model_computed_type(self):
        """Test EscalationPolicy model computed type property."""
        escalation_rule = EscalationRule(
            escalation_delay_in_minutes=30,
            targets=[
                EscalationTarget(
                    id="USER123",
                    type="user_reference",
                    summary="Test User",
                )
            ],
        )

        policy = EscalationPolicy(
            id="EP123",
            summary="Test Policy Summary",
            name="Test Policy",
            escalation_rules=[escalation_rule],
        )

        self.assertEqual(policy.type, "escalation_policy")


if __name__ == "__main__":
    unittest.main()
