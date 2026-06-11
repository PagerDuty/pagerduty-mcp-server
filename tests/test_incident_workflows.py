"""Unit tests for incident workflow tools."""

import unittest
from unittest.mock import Mock, patch

from pagerduty_mcp.models import (
    IncidentReference,
    IncidentWorkflow,
    IncidentWorkflowInstance,
    IncidentWorkflowInstanceCreate,
    IncidentWorkflowInstanceRequest,
    IncidentWorkflowQuery,
    ListResponseModel,
)
from pagerduty_mcp.tools.incident_workflows import (
    get_incident_workflow,
    list_incident_workflows,
    start_incident_workflow,
)


class TestIncidentWorkflowTools(unittest.TestCase):
    """Test cases for incident workflow tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_workflow_data = {
            "id": "PSFEVL7",
            "name": "Example Incident Workflow",
            "description": "This Incident Workflow is an example",
            "type": "incident_workflow",
            "created_at": "2022-12-13T19:55:01.171Z",
            "self": "https://api.pagerduty.com/incident_workflows/PSFEVL7",
            "html_url": "https://pdt-flex-actions.pagerduty.com/flex-workflows/workflows/PSFEVL7",
            "is_enabled": True,
        }

        cls.sample_workflow_with_steps = {
            "id": "PSFEVL7",
            "name": "Example Incident Workflow",
            "description": "This Incident Workflow is an example",
            "type": "incident_workflow",
            "created_at": "2022-12-13T19:55:01.171Z",
            "self": "https://api.pagerduty.com/incident_workflows/PSFEVL7",
            "html_url": "https://pdt-flex-actions.pagerduty.com/flex-workflows/workflows/PSFEVL7",
            "is_enabled": True,
            "steps": [
                {
                    "id": "P4RG7YW",
                    "type": "step",
                    "name": "Send Status Update",
                    "description": "Posts a status update to a given incident",
                    "action_configuration": {
                        "action_id": "pagerduty.com:incident-workflows:send-status-update:1",
                        "description": "Posts a status update to a given incident",
                        "inputs": [
                            {
                                "name": "Message",
                                "parameter_type": "text",
                                "value": "Example status message sent on {{current_date}}",
                            }
                        ],
                        "outputs": [
                            {"name": "Result", "reference_name": "result", "parameter_type": "text"},
                            {"name": "Result Summary", "reference_name": "result-summary", "parameter_type": "text"},
                            {"name": "Error", "reference_name": "error", "parameter_type": "text"},
                        ],
                    },
                }
            ],
        }

        cls.sample_instance_data = {
            "id": "P3SNKQS",
            "type": "incident_workflow_instance",
            "incident": {
                "id": "Q1R2DLCB21K7NP",
                "type": "incident_reference",
                "summary": "[#1234] The server is on fire.",
                "self": "https://api.pagerduty.com/incidents/PT4KHLK",
                "html_url": "https://subdomain.pagerduty.com/incidents/PT4KHLK",
            },
        }

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    @patch("pagerduty_mcp.tools.incident_workflows.paginate")
    def test_list_incident_workflows_basic(self, mock_paginate, mock_get_client):
        """Test basic workflow listing."""
        mock_paginate.return_value = [self.sample_workflow_data]

        query = IncidentWorkflowQuery()
        result = list_incident_workflows(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], IncidentWorkflow)
        self.assertEqual(result.response[0].id, "PSFEVL7")
        self.assertEqual(result.response[0].name, "Example Incident Workflow")
        self.assertTrue(result.response[0].is_enabled)

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    @patch("pagerduty_mcp.tools.incident_workflows.paginate")
    def test_list_incident_workflows_with_query(self, mock_paginate, mock_get_client):
        """Test workflow listing with query filter."""
        mock_paginate.return_value = [self.sample_workflow_data]

        query = IncidentWorkflowQuery(query="example", limit=10)
        result = list_incident_workflows(query)

        self.assertEqual(len(result.response), 1)
        mock_paginate.assert_called_once()
        call_args = mock_paginate.call_args
        self.assertEqual(call_args.kwargs["params"]["query"], "example")
        self.assertEqual(call_args.kwargs["maximum_records"], 10)

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    @patch("pagerduty_mcp.tools.incident_workflows.paginate")
    def test_list_incident_workflows_with_include(self, mock_paginate, mock_get_client):
        """Test workflow listing with include parameter."""
        mock_paginate.return_value = [self.sample_workflow_with_steps]

        query = IncidentWorkflowQuery(include=["steps", "team"])
        result = list_incident_workflows(query)

        self.assertEqual(len(result.response), 1)
        self.assertIsNotNone(result.response[0].steps)
        self.assertEqual(len(result.response[0].steps), 1)
        self.assertEqual(result.response[0].steps[0].name, "Send Status Update")

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    @patch("pagerduty_mcp.tools.incident_workflows.paginate")
    def test_list_incident_workflows_empty(self, mock_paginate, mock_get_client):
        """Test workflow listing with empty results."""
        mock_paginate.return_value = []

        query = IncidentWorkflowQuery()
        result = list_incident_workflows(query)

        self.assertEqual(len(result.response), 0)

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    @patch("pagerduty_mcp.tools.incident_workflows.paginate")
    def test_list_incident_workflows_no_parameters(self, mock_paginate, mock_get_client):
        """Test workflow listing with no parameters (None)."""
        mock_paginate.return_value = [self.sample_workflow_data]

        result = list_incident_workflows()

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], IncidentWorkflow)
        self.assertEqual(result.response[0].id, "PSFEVL7")
        mock_paginate.assert_called_once()
        call_args = mock_paginate.call_args
        self.assertEqual(call_args.kwargs["maximum_records"], 100)

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    @patch("pagerduty_mcp.tools.incident_workflows.paginate")
    def test_list_incident_workflows_explicit_none(self, mock_paginate, mock_get_client):
        """Test workflow listing with explicit None parameter."""
        mock_paginate.return_value = [self.sample_workflow_data]

        result = list_incident_workflows(None)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        mock_paginate.assert_called_once()
        call_args = mock_paginate.call_args
        self.assertEqual(call_args.kwargs["maximum_records"], 100)

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_get_incident_workflow_success(self, mock_get_client):
        """Test getting a specific workflow successfully."""
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_workflow_with_steps
        mock_get_client.return_value = mock_client

        result = get_incident_workflow("PSFEVL7")

        self.assertIsInstance(result, IncidentWorkflow)
        self.assertEqual(result.id, "PSFEVL7")
        self.assertEqual(result.name, "Example Incident Workflow")
        self.assertIsNotNone(result.steps)
        self.assertEqual(len(result.steps), 1)
        mock_client.rget.assert_called_once_with("/incident_workflows/PSFEVL7")

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_get_incident_workflow_wrapped_response(self, mock_get_client):
        """Test getting a workflow with wrapped response."""
        mock_client = Mock()
        mock_client.rget.return_value = {"incident_workflow": self.sample_workflow_data}
        mock_get_client.return_value = mock_client

        result = get_incident_workflow("PSFEVL7")

        self.assertIsInstance(result, IncidentWorkflow)
        self.assertEqual(result.id, "PSFEVL7")
        self.assertEqual(result.name, "Example Incident Workflow")

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_get_incident_workflow_unwrapped_response(self, mock_get_client):
        """Test getting a workflow with unwrapped response."""
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_workflow_data
        mock_get_client.return_value = mock_client

        result = get_incident_workflow("PSFEVL7")

        self.assertIsInstance(result, IncidentWorkflow)
        self.assertEqual(result.id, "PSFEVL7")

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_start_incident_workflow_success(self, mock_get_client):
        """Test starting a workflow successfully."""
        mock_client = Mock()
        mock_client.rpost.return_value = self.sample_instance_data
        mock_get_client.return_value = mock_client

        incident_ref = IncidentReference(id="Q1R2DLCB21K7NP")
        instance_create = IncidentWorkflowInstanceCreate(incident=incident_ref)
        request = IncidentWorkflowInstanceRequest(incident_workflow_instance=instance_create)

        result = start_incident_workflow("PSFEVL7", request)

        self.assertIsInstance(result, IncidentWorkflowInstance)
        self.assertEqual(result.id, "P3SNKQS")
        self.assertEqual(result.incident.id, "Q1R2DLCB21K7NP")
        mock_client.rpost.assert_called_once()

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_start_incident_workflow_wrapped_response(self, mock_get_client):
        """Test starting a workflow with wrapped response."""
        mock_client = Mock()
        mock_client.rpost.return_value = {"incident_workflow_instance": self.sample_instance_data}
        mock_get_client.return_value = mock_client

        incident_ref = IncidentReference(id="Q1R2DLCB21K7NP")
        instance_create = IncidentWorkflowInstanceCreate(incident=incident_ref)
        request = IncidentWorkflowInstanceRequest(incident_workflow_instance=instance_create)

        result = start_incident_workflow("PSFEVL7", request)

        self.assertIsInstance(result, IncidentWorkflowInstance)
        self.assertEqual(result.id, "P3SNKQS")

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_start_incident_workflow_unwrapped_response(self, mock_get_client):
        """Test starting a workflow with unwrapped response."""
        mock_client = Mock()
        mock_client.rpost.return_value = self.sample_instance_data
        mock_get_client.return_value = mock_client

        incident_ref = IncidentReference(id="Q1R2DLCB21K7NP")
        instance_create = IncidentWorkflowInstanceCreate(incident=incident_ref)
        request = IncidentWorkflowInstanceRequest(incident_workflow_instance=instance_create)

        result = start_incident_workflow("PSFEVL7", request)

        self.assertIsInstance(result, IncidentWorkflowInstance)
        self.assertEqual(result.id, "P3SNKQS")

    @patch("pagerduty_mcp.tools.incident_workflows.get_client")
    def test_start_incident_workflow_with_custom_id(self, mock_get_client):
        """Test starting a workflow with custom instance ID."""
        mock_client = Mock()
        instance_data_with_custom_id = self.sample_instance_data.copy()
        instance_data_with_custom_id["id"] = "CUSTOM123"
        mock_client.rpost.return_value = instance_data_with_custom_id
        mock_get_client.return_value = mock_client

        incident_ref = IncidentReference(id="Q1R2DLCB21K7NP")
        instance_create = IncidentWorkflowInstanceCreate(id="CUSTOM123", incident=incident_ref)
        request = IncidentWorkflowInstanceRequest(incident_workflow_instance=instance_create)

        result = start_incident_workflow("PSFEVL7", request)

        self.assertIsInstance(result, IncidentWorkflowInstance)
        self.assertEqual(result.id, "CUSTOM123")

    def test_incident_workflow_model_computed_type(self):
        """Test that IncidentWorkflow model has correct computed type."""
        workflow = IncidentWorkflow(**self.sample_workflow_data)
        self.assertEqual(workflow.type, "incident_workflow")

    def test_incident_workflow_instance_model_computed_type(self):
        """Test that IncidentWorkflowInstance model has correct computed type."""
        from pagerduty_mcp.models import IncidentWorkflowInstance

        instance = IncidentWorkflowInstance(**self.sample_instance_data)
        self.assertEqual(instance.type, "incident_workflow_instance")

    def test_step_model_computed_type(self):
        """Test that Step model has correct computed type."""
        from pagerduty_mcp.models import Step

        step_data = self.sample_workflow_with_steps["steps"][0]
        step = Step(**step_data)
        self.assertEqual(step.type, "step")

    def test_incident_workflow_from_api_response_wrapped(self):
        """Test IncidentWorkflow.from_api_response with wrapped response."""
        wrapped = {"incident_workflow": self.sample_workflow_data}
        workflow = IncidentWorkflow.from_api_response(wrapped)
        self.assertIsInstance(workflow, IncidentWorkflow)
        self.assertEqual(workflow.id, "PSFEVL7")

    def test_incident_workflow_from_api_response_unwrapped(self):
        """Test IncidentWorkflow.from_api_response with unwrapped response."""
        workflow = IncidentWorkflow.from_api_response(self.sample_workflow_data)
        self.assertIsInstance(workflow, IncidentWorkflow)
        self.assertEqual(workflow.id, "PSFEVL7")

    def test_incident_workflow_instance_from_api_response_wrapped(self):
        """Test IncidentWorkflowInstance.from_api_response with wrapped response."""
        wrapped = {"incident_workflow_instance": self.sample_instance_data}
        instance = IncidentWorkflowInstance.from_api_response(wrapped)
        self.assertIsInstance(instance, IncidentWorkflowInstance)
        self.assertEqual(instance.id, "P3SNKQS")

    def test_incident_workflow_instance_from_api_response_unwrapped(self):
        """Test IncidentWorkflowInstance.from_api_response with unwrapped response."""
        instance = IncidentWorkflowInstance.from_api_response(self.sample_instance_data)
        self.assertIsInstance(instance, IncidentWorkflowInstance)
        self.assertEqual(instance.id, "P3SNKQS")


if __name__ == "__main__":
    unittest.main()
