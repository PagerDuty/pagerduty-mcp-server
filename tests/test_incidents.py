"""Unit tests for incident tools."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from mcp.server.fastmcp import Context

from pagerduty_mcp.models import (
    MAX_RESULTS,
    Incident,
    IncidentCreate,
    IncidentCreateRequest,
    IncidentManageRequest,
    IncidentNote,
    IncidentQuery,
    IncidentResponderRequest,
    IncidentResponderRequestResponse,
    ListResponseModel,
    MCPContext,
    ServiceReference,
    UserReference,
)
from pagerduty_mcp.tools.incidents import (
    _change_incident_status,
    _change_incident_urgency,
    _escalate_incident,
    _generate_manage_request,
    _reassign_incident,
    _update_manage_request,
    add_note_to_incident,
    add_responders,
    create_incident,
    get_incident,
    list_incidents,
    manage_incidents,
)


class TestIncidentTools(unittest.TestCase):
    """Test cases for incident tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_incident_data = {
            "id": "PINCIDENT123",
            "incident_number": 123,
            "title": "Test Incident",
            "description": "Test Description",
            "status": "triggered",
            "urgency": "high",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "service": {"id": "PSERVICE123", "type": "service_reference"},
            "assignments": [],
            "escalation_policy": {"id": "PESC123", "type": "escalation_policy_reference"},
            "teams": [],
            "alert_counts": {"all": 0, "triggered": 0, "resolved": 0},
            "incident_key": "test-key",
            "html_url": "https://test.pagerduty.com/incidents/PINCIDENT123",
        }

        cls.sample_user_data = Mock()
        cls.sample_user_data.id = "PUSER123"
        cls.sample_user_data.teams = [Mock(id="PTEAM123")]

    @patch("pagerduty_mcp.tools.incidents.get_client")
    @patch("pagerduty_mcp.tools.incidents.get_user_data")
    @patch("pagerduty_mcp.tools.incidents.paginate")
    def test_list_incidents_basic(self, mock_paginate, mock_get_user_data, mock_get_client):
        """Test basic incident listing."""
        # Setup mocks
        mock_paginate.return_value = [self.sample_incident_data]
        mock_get_user_data.return_value = self.sample_user_data

        # Test with basic query
        query = IncidentQuery()
        result = list_incidents(query)

        # Assertions
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], Incident)
        self.assertEqual(result.response[0].id, "PINCIDENT123")

        # Verify paginate was called with correct parameters
        mock_paginate.assert_called_once()
        call_args = mock_paginate.call_args
        self.assertEqual(call_args[1]["entity"], "incidents")
        self.assertEqual(call_args[1]["maximum_records"], MAX_RESULTS)

    @patch("pagerduty_mcp.tools.incidents.get_client")
    @patch("pagerduty_mcp.tools.incidents.get_user_data")
    @patch("pagerduty_mcp.tools.incidents.paginate")
    def test_list_incidents_assigned_scope(self, mock_paginate, mock_get_user_data, mock_get_client):
        """Test listing incidents with assigned scope."""
        # Setup mocks
        mock_paginate.return_value = [self.sample_incident_data]
        mock_get_user_data.return_value = self.sample_user_data

        # Test with assigned scope
        query = IncidentQuery(request_scope="assigned")
        _ = list_incidents(query)

        # Verify user_ids parameter was added
        call_args = mock_paginate.call_args
        self.assertIn("user_ids[]", call_args[1]["params"])
        self.assertEqual(call_args[1]["params"]["user_ids[]"], ["PUSER123"])

    @patch("pagerduty_mcp.tools.incidents.get_client")
    @patch("pagerduty_mcp.tools.incidents.get_user_data")
    @patch("pagerduty_mcp.tools.incidents.paginate")
    def test_list_incidents_teams_scope(self, mock_paginate, mock_get_user_data, mock_get_client):
        """Test listing incidents with teams scope."""
        # Setup mocks
        mock_paginate.return_value = [self.sample_incident_data]
        mock_get_user_data.return_value = self.sample_user_data

        # Test with teams scope
        query = IncidentQuery(request_scope="teams")
        _ = list_incidents(query)

        # Verify teams_ids parameter was added
        call_args = mock_paginate.call_args
        self.assertIn("teams_ids[]", call_args[1]["params"])
        self.assertEqual(call_args[1]["params"]["teams_ids[]"], ["PTEAM123"])

    @patch("pagerduty_mcp.tools.incidents.get_client")
    @patch("pagerduty_mcp.tools.incidents.get_user_data")
    @patch("pagerduty_mcp.tools.incidents.paginate")
    def test_list_incidents_with_filters(self, mock_paginate, mock_get_user_data, mock_get_client):
        """Test listing incidents with various filters."""
        # Setup mocks
        mock_paginate.return_value = [self.sample_incident_data]
        mock_get_user_data.return_value = self.sample_user_data

        # Test with filters
        since_date = datetime(2023, 1, 1)
        query = IncidentQuery(status=["triggered", "acknowledged"], since=since_date, urgencies=["high"], limit=50)
        _ = list_incidents(query)

        # Verify parameters were passed correctly
        call_args = mock_paginate.call_args
        params = call_args[1]["params"]
        self.assertIn("statuses[]", params)
        self.assertIn("since", params)
        self.assertIn("urgencies[]", params)

        self.assertEqual(call_args[1]["maximum_records"], 50)
        self.assertEqual(params["statuses[]"], ["triggered", "acknowledged"])
        self.assertEqual(params["since"], since_date.isoformat())
        self.assertEqual(params["urgencies[]"], ["high"])

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_get_incident_success(self, mock_get_client):
        """Test getting a specific incident successfully."""
        # Setup mock
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_incident_data
        mock_get_client.return_value = mock_client

        # Test
        result = get_incident("PINCIDENT123")

        # Assertions
        self.assertIsInstance(result, Incident)
        self.assertEqual(result.id, "PINCIDENT123")
        mock_client.rget.assert_called_once_with("/incidents/PINCIDENT123")

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_get_incident_api_error(self, mock_get_client):
        """Test get_incident with API error."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client.rget.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        # Test that exception is raised
        with self.assertRaises(Exception) as context:
            get_incident("PINCIDENT123")

        self.assertIn("API Error", str(context.exception))

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_create_incident_success(self, mock_get_client):
        """Test creating an incident successfully."""
        # Setup mock
        mock_client = Mock()
        mock_client.rpost.return_value = self.sample_incident_data
        mock_get_client.return_value = mock_client

        # Create test request
        incident_data = IncidentCreate(
            title="Test Incident", service=ServiceReference(id="PSERVICE123"), urgency="high"
        )
        create_request = IncidentCreateRequest(incident=incident_data)

        # Test
        result = create_incident(create_request)

        # Assertions
        self.assertIsInstance(result, Incident)
        self.assertEqual(result.id, "PINCIDENT123")
        mock_client.rpost.assert_called_once()
        call_args = mock_client.rpost.call_args
        self.assertEqual(call_args[0][0], "/incidents")
        self.assertIn("json", call_args[1])

    def test_generate_manage_request(self):
        """Test _generate_manage_request helper function."""
        incident_ids = ["PINC1", "PINC2"]
        result = _generate_manage_request(incident_ids)

        expected = {
            "incidents": [
                {"type": "incident_reference", "id": "PINC1"},
                {"type": "incident_reference", "id": "PINC2"},
            ]
        }
        self.assertEqual(result, expected)

    def test_update_manage_request(self):
        """Test _update_manage_request helper function."""
        request = {
            "incidents": [
                {"type": "incident_reference", "id": "PINC1"},
                {"type": "incident_reference", "id": "PINC2"},
            ]
        }

        result = _update_manage_request(request, "status", "acknowledged")

        # Verify all incidents got the new field
        for incident in result["incidents"]:
            self.assertEqual(incident["status"], "acknowledged")

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_change_incident_status(self, mock_get_client):
        """Test _change_incident_status helper function."""
        # Setup mock
        mock_client = Mock()
        mock_client.rput.return_value = [self.sample_incident_data]
        mock_get_client.return_value = mock_client

        # Test
        _change_incident_status(["PINC1"], "acknowledged")

        # Assertions
        mock_client.rput.assert_called_once_with(
            "/incidents", json={"incidents": [{"type": "incident_reference", "id": "PINC1", "status": "acknowledged"}]}
        )

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_change_incident_urgency(self, mock_get_client):
        """Test _change_incident_urgency helper function."""
        # Setup mock
        mock_client = Mock()
        mock_client.rput.return_value = [self.sample_incident_data]
        mock_get_client.return_value = mock_client

        # Test
        _change_incident_urgency(["PINC1"], "low")

        # Assertions
        mock_client.rput.assert_called_once_with(
            "/incidents", json={"incidents": [{"type": "incident_reference", "id": "PINC1", "urgency": "low"}]}
        )

    @patch("pagerduty_mcp.tools.incidents.get_client")
    @patch("pagerduty_mcp.tools.incidents.datetime")
    def test_reassign_incident(self, mock_datetime, mock_get_client):
        """Test _reassign_incident helper function."""
        # Setup mocks
        mock_client = Mock()
        mock_client.rput.return_value = [self.sample_incident_data]
        mock_get_client.return_value = mock_client

        mock_now = Mock()
        mock_now.isoformat.return_value = "2023-01-01T00:00:00"
        mock_datetime.now.return_value = mock_now

        # Test
        assignee = UserReference(id="PUSER123")
        _reassign_incident(["PINC1"], assignee)

        # Verify the request structure
        call_args = mock_client.rput.call_args
        json_data = call_args[1]["json"]
        self.assertIn("incidents", json_data)
        incident = json_data["incidents"][0]
        self.assertEqual(incident["id"], "PINC1")
        self.assertIn("assignments", incident)
        assignment = incident["assignments"][0]
        self.assertEqual(assignment["assignee"]["id"], "PUSER123")

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_escalate_incident(self, mock_get_client):
        """Test _escalate_incident helper function."""
        # Setup mock
        mock_client = Mock()
        mock_client.rput.return_value = [self.sample_incident_data]
        mock_get_client.return_value = mock_client

        # Test
        _escalate_incident(["PINC1"], 2)

        # Assertions
        mock_client.rput.assert_called_once_with(
            "/incidents", json={"incidents": [{"type": "incident_reference", "id": "PINC1", "escalation_level": 2}]}
        )

    @patch("pagerduty_mcp.tools.incidents._change_incident_status")
    def test_manage_incidents_status_change(self, mock_change_status):
        """Test manage_incidents with status change."""
        # Setup mock
        mock_change_status.return_value = [self.sample_incident_data]

        # Test
        manage_request = IncidentManageRequest(incident_ids=["PINC1"], status="acknowledged")
        result = manage_incidents(manage_request)

        # Assertions
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        mock_change_status.assert_called_once_with(["PINC1"], "acknowledged")

    @patch("pagerduty_mcp.tools.incidents._change_incident_urgency")
    def test_manage_incidents_urgency_change(self, mock_change_urgency):
        """Test manage_incidents with urgency change."""
        # Setup mock
        mock_change_urgency.return_value = [self.sample_incident_data]

        # Test
        manage_request = IncidentManageRequest(incident_ids=["PINC1"], urgency="low")
        result = manage_incidents(manage_request)

        # Assertions
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        mock_change_urgency.assert_called_once_with(["PINC1"], "low")

    @patch("pagerduty_mcp.tools.incidents._reassign_incident")
    def test_manage_incidents_reassignment(self, mock_reassign):
        """Test manage_incidents with reassignment."""
        # Setup mock
        mock_reassign.return_value = [self.sample_incident_data]

        # Test
        assignee = UserReference(id="PUSER123")
        manage_request = IncidentManageRequest(
            incident_ids=["PINC1"],
            assignement=assignee,  # Note: typo in original code "assignement"
        )
        result = manage_incidents(manage_request)

        # Assertions
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        mock_reassign.assert_called_once_with(["PINC1"], assignee)

    @patch("pagerduty_mcp.tools.incidents._escalate_incident")
    def test_manage_incidents_escalation(self, mock_escalate):
        """Test manage_incidents with escalation."""
        # Setup mock
        mock_escalate.return_value = [self.sample_incident_data]

        # Test
        manage_request = IncidentManageRequest(incident_ids=["PINC1"], escalation_level=2)
        result = manage_incidents(manage_request)

        # Assertions
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        mock_escalate.assert_called_once_with(["PINC1"], 2)

    def test_manage_incidents_no_actions(self):
        """Test manage_incidents with no actions specified."""
        # Test
        manage_request = IncidentManageRequest(incident_ids=["PINC1"])
        result = manage_incidents(manage_request)

        # Should return empty response
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_add_responders_success(self, mock_get_client):
        """Test add_responders successfully."""
        # Setup mock
        mock_client = Mock()
        mock_response = {
            "responder_request": {
                "requester": {"id": "PUSER123", "type": "user_reference"},
                "message": "Help needed",
                "requested_at": "2023-01-01T00:00:00Z",
                "responder_request_targets": [],
            }
        }
        mock_client.rpost.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Setup context
        context = Mock(spec=Context)
        mcp_context = Mock(spec=MCPContext)
        user_mock = Mock()
        user_mock.id = "PUSER123"
        mcp_context.user = user_mock
        context.request_context.lifespan_context = mcp_context

        # Test - create minimal request
        request = IncidentResponderRequest(requester_id="PUSER123", message="Help needed", responder_request_targets=[])
        result = add_responders("PINC1", request, context)

        # Assertions
        self.assertIsInstance(result, IncidentResponderRequestResponse)
        mock_client.rpost.assert_called_once()
        call_args = mock_client.rpost.call_args
        self.assertEqual(call_args[0][0], "/incidents/PINC1/responder_requests")

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_add_responders_no_user_context(self, mock_get_client):
        """Test add_responders with no user context."""
        # Setup context without user
        context = Mock(spec=Context)
        mcp_context = Mock(spec=MCPContext)
        mcp_context.user = None
        context.request_context.lifespan_context = mcp_context

        # Test
        request = IncidentResponderRequest(requester_id="PUSER123", message="Help needed", responder_request_targets=[])
        result = add_responders("PINC1", request, context)

        # Should return error message
        self.assertIsInstance(result, str)
        self.assertIn("Cannot add responders with account level auth", result)

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_add_responders_unexpected_response(self, mock_get_client):
        """Test add_responders with unexpected response format."""
        # Setup mock with unexpected response
        mock_client = Mock()
        mock_client.rpost.return_value = "Unexpected response"
        mock_get_client.return_value = mock_client

        # Setup context
        context = Mock(spec=Context)
        mcp_context = Mock(spec=MCPContext)
        user_mock = Mock()
        user_mock.id = "PUSER123"
        mcp_context.user = user_mock
        context.request_context.lifespan_context = mcp_context

        # Test
        request = IncidentResponderRequest(requester_id="PUSER123", message="Help needed", responder_request_targets=[])
        result = add_responders("PINC1", request, context)

        # Should return error message
        self.assertIsInstance(result, str)
        self.assertIn("Unexpected response format", result)

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_add_responders_mixed_targets_payload(self, mock_get_client):
        """Ensure payload includes both user and escalation policy targets with proper types."""
        # Setup mock client response to match expected shape
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "responder_request": {
                "requester": {"id": "PUSER123", "type": "user_reference"},
                "message": "Help needed",
                "requested_at": "2023-01-01T00:00:00Z",
                "responder_request_targets": [],
            }
        }
        mock_get_client.return_value = mock_client

        # Build request with mixed targets
        from pagerduty_mcp.models import (
            IncidentResponderRequest,
            ResponderRequest,
            ResponderRequestTarget,
        )

        user_target = ResponderRequestTarget(
            responder_request_target=ResponderRequest(id="PUSER999", type="user_reference")
        )
        ep_target = ResponderRequestTarget(
            responder_request_target=ResponderRequest(id="PESC123", type="escalation_policy_reference")
        )

        request = IncidentResponderRequest(
            requester_id="PUSER123",
            message="Help needed",
            responder_request_targets=[user_target, ep_target],
        )

        # Context with user info
        context = Mock(spec=Context)
        mcp_context = Mock(spec=MCPContext)
        user_mock = Mock()
        user_mock.id = "PUSER123"
        mcp_context.user = user_mock
        context.request_context.lifespan_context = mcp_context

        # Execute
        _ = add_responders("PINC1", request, context)

        # Validate payload structure and types
        call_args = mock_client.rpost.call_args
        self.assertEqual(call_args[0][0], "/incidents/PINC1/responder_requests")
        payload = call_args[1]["json"]
        self.assertIn("responder_request_targets", payload)
        self.assertEqual(len(payload["responder_request_targets"]), 2)

        first = payload["responder_request_targets"][0]["responder_request_target"]
        second = payload["responder_request_targets"][1]["responder_request_target"]
        self.assertEqual(first["type"], "user_reference")
        self.assertEqual(first["id"], "PUSER999")
        self.assertEqual(second["type"], "escalation_policy_reference")
        self.assertEqual(second["id"], "PESC123")

    @patch("pagerduty_mcp.tools.incidents.get_client")
    def test_add_note_to_incident_success(self, mock_get_client):
        """Test successfully adding a note to an incident."""
        # Setup mock response
        mock_response = {
            "id": "PNOTE123",
            "content": "This is a test note",
            "created_at": "2023-01-01T10:00:00Z",
            "user": {"id": "PUSER123", "summary": "Test User"},
        }

        mock_client = Mock()
        mock_client.rpost.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Test
        result = add_note_to_incident("PINC123", "This is a test note")

        # Assertions
        self.assertIsInstance(result, IncidentNote)
        self.assertEqual(result.id, "PNOTE123")
        self.assertEqual(result.content, "This is a test note")
        self.assertEqual(result.user.id, "PUSER123")

        # Verify API call
        mock_client.rpost.assert_called_once_with(
            "/incidents/PINC123/notes", json={"note": {"content": "This is a test note"}}
        )

    def test_incidentquery_reject_statuses_param(self):
        """Ensure providing 'statuses' yields a clear validation error."""
        from pydantic import ValidationError

        with self.assertRaises(ValidationError) as ctx:
            IncidentQuery.model_validate({"statuses": ["triggered", "acknowledged"]})

        self.assertIn(
            'The correct parameter to filter by multiple Incidents statuses is "status", not "statuses"',
            str(ctx.exception),
        )


if __name__ == "__main__":
    unittest.main()
