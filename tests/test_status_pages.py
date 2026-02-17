"""Unit tests for Status Pages tools."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from tests.context_test_case import ContextTestCase
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.status_pages import (
    StatusPage,
    StatusPageImpact,
    StatusPageImpactQuery,
    StatusPageImpactReference,
    StatusPagePost,
    StatusPagePostCreateRequest,
    StatusPagePostCreateRequestWrapper,
    StatusPagePostQuery,
    StatusPagePostReference,
    StatusPagePostUpdate,
    StatusPagePostUpdateImpact,
    StatusPagePostUpdateQuery,
    StatusPagePostUpdateRequest,
    StatusPagePostUpdateRequestWrapper,
    StatusPageQuery,
    StatusPageReference,
    StatusPageServiceReference,
    StatusPageSeverity,
    StatusPageSeverityQuery,
    StatusPageSeverityReference,
    StatusPageStatus,
    StatusPageStatusQuery,
    StatusPageStatusReference,
)
from pagerduty_mcp.tools.status_pages import (
    create_status_page_post,
    create_status_page_post_update,
    get_status_page_post,
    list_status_page_impacts,
    list_status_page_post_updates,
    list_status_page_severities,
    list_status_page_statuses,
    list_status_pages,
)


class TestStatusPagesTools(ContextTestCase):
    """Test cases for Status Pages tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        cls.sample_status_page_data = {
            "id": "PT4KHLK",
            "name": "My brand Status Page",
            "published_at": "2017-09-13T10:11:12Z",
            "status_page_type": "private",
            "type": "status_page",
            "url": "https://status.mybrand.example",
        }

        cls.sample_severity_data = {
            "id": "PIJ90N7",
            "self": "https://api.pagerduty.com/status_pages/PQ8W0D0/severities/PIJ90N7",
            "description": "all good",
            "post_type": "incident",
            "status_page": {"id": "PQ8W0D0", "type": "status_page"},
            "type": "status_page_severity",
        }

        cls.sample_impact_data = {
            "id": "PIJ90N7",
            "self": "https://api.pagerduty.com/status_pages/PQ8W0D0/impacts/PIJ90N7",
            "description": "operational",
            "post_type": "incident",
            "status_page": {"id": "PQ8W0D0", "type": "status_page"},
            "type": "status_page_impact",
        }

        cls.sample_status_data = {
            "id": "PIJ90N7",
            "self": "https://api.pagerduty.com/status_pages/PQ8W0D0/statuses/PIJ90N7",
            "description": "investigating",
            "post_type": "incident",
            "status_page": {"id": "PQ8W0D0", "type": "status_page"},
            "type": "status_page_status",
        }

        cls.sample_post_data = {
            "id": "PIJ90N7",
            "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/PIJ90N7",
            "type": "status_page_post",
            "post_type": "maintenance",
            "status_page": {"id": "PR5LMML", "type": "status_page"},
            "title": "maintenance window for database upgrade",
            "starts_at": "2023-12-12T11:00:00Z",
            "ends_at": "2023-12-12T11:00:00Z",
            "updates": [{"id": "P7HUBBZ", "type": "status_page_post_update"}],
        }

        cls.sample_post_update_data = {
            "id": "PXSOCH0",
            "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/P6F2CJ3/post_updates/PXSOCH0",
            "post": {"id": "P6F2CJ3", "type": "status_page_post"},
            "message": "<p>We will be undergoing schedule maintenance at this date and time</p>",
            "reviewed_status": "approved",
            "status": {"id": "P6F2CJ3", "type": "status_page_status"},
            "severity": {"id": "P6F2CJ4", "type": "status_page_severity"},
            "impacted_services": [
                {
                    "service": {"id": "PYHMEI3", "type": "status_page_service"},
                    "impact": {"id": "PY5OM08", "type": "status_page_impact"},
                }
            ],
            "update_frequency_ms": 300000,
            "notify_subscribers": False,
            "reported_at": "2023-12-12T10:08:19Z",
            "type": "status_page_post_update",
        }

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_pages_basic(self, mock_paginate):
        """Test basic Status Pages listing."""
        mock_paginate.return_value = [self.sample_status_page_data]

        query = StatusPageQuery()
        result = list_status_pages(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPage)
        self.assertEqual(result.response[0].id, "PT4KHLK")
        self.assertEqual(result.response[0].name, "My brand Status Page")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_pages_filter_by_type(self, mock_paginate):
        """Test Status Pages listing with type filter."""
        mock_paginate.return_value = [self.sample_status_page_data]

        query = StatusPageQuery(status_page_type="private")
        result = list_status_pages(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].status_page_type, "private")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_severities_basic(self, mock_paginate):
        """Test basic Severity listing."""
        mock_paginate.return_value = [self.sample_severity_data]

        query = StatusPageSeverityQuery()
        result = list_status_page_severities("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPageSeverity)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[0].description, "all good")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_severities_filter_by_post_type(self, mock_paginate):
        """Test Severity listing with post type filter."""
        mock_paginate.return_value = [self.sample_severity_data]

        query = StatusPageSeverityQuery(post_type="incident")
        result = list_status_page_severities("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].post_type, "incident")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_impacts_basic(self, mock_paginate):
        """Test basic Impact listing."""
        mock_paginate.return_value = [self.sample_impact_data]

        query = StatusPageImpactQuery()
        result = list_status_page_impacts("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPageImpact)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[0].description, "operational")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_impacts_filter_by_post_type(self, mock_paginate):
        """Test Impact listing with post type filter."""
        mock_paginate.return_value = [self.sample_impact_data]

        query = StatusPageImpactQuery(post_type="incident")
        result = list_status_page_impacts("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].post_type, "incident")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_statuses_basic(self, mock_paginate):
        """Test basic Status listing."""
        mock_paginate.return_value = [self.sample_status_data]

        query = StatusPageStatusQuery()
        result = list_status_page_statuses("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPageStatus)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[0].description, "investigating")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_statuses_filter_by_post_type(self, mock_paginate):
        """Test Status listing with post type filter."""
        mock_paginate.return_value = [self.sample_status_data]

        query = StatusPageStatusQuery(post_type="incident")
        result = list_status_page_statuses("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].post_type, "incident")

    def test_create_status_page_post_success(self):
        """Test creating a Status Page Post successfully."""
        self.mock_client.rpost.return_value = {"post": self.sample_post_data}

        update = StatusPagePostUpdateRequest(
            message="<p>Scheduled maintenance</p>",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            impacted_services=[
                StatusPagePostUpdateImpact(
                    service=StatusPageServiceReference(id="PYHMEI3"),
                    impact=StatusPageImpactReference(id="PY5OM08"),
                )
            ],
            notify_subscribers=False,
            update_frequency_ms=None,
        )

        post_request = StatusPagePostCreateRequest(
            title="Database Upgrade",
            post_type="maintenance",
            starts_at=datetime(2023, 12, 12, 11, 0, 0),
            ends_at=datetime(2023, 12, 12, 12, 0, 0),
            updates=[update],
            status_page=StatusPageReference(id="PR5LMML"),
        )

        wrapper = StatusPagePostCreateRequestWrapper(post=post_request)
        result = create_status_page_post("PR5LMML", wrapper)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")
        self.mock_client.rpost.assert_called_once()

    def test_create_status_page_post_unwrapped_response(self):
        """Test creating a Status Page Post with unwrapped response."""
        self.mock_client.rpost.return_value = self.sample_post_data

        update = StatusPagePostUpdateRequest(
            message="<p>Scheduled maintenance</p>",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            impacted_services=[],
            notify_subscribers=False,
            update_frequency_ms=None,
        )

        post_request = StatusPagePostCreateRequest(
            title="Database Upgrade",
            post_type="maintenance",
            starts_at=datetime(2023, 12, 12, 11, 0, 0),
            ends_at=datetime(2023, 12, 12, 12, 0, 0),
            updates=[update],
            status_page=StatusPageReference(id="PR5LMML"),
        )

        wrapper = StatusPagePostCreateRequestWrapper(post=post_request)
        result = create_status_page_post("PR5LMML", wrapper)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")

    def test_get_status_page_post_success(self):
        """Test getting a Status Page Post successfully."""
        self.mock_client.rget.return_value = {"post": self.sample_post_data}

        query = StatusPagePostQuery()
        result = get_status_page_post("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")
        self.mock_client.rget.assert_called_once()

    def test_get_status_page_post_with_includes(self):
        """Test getting a Status Page Post with included resources."""
        self.mock_client.rget.return_value = {"post": self.sample_post_data}

        query = StatusPagePostQuery(include=["status_page_post_update"])
        result = get_status_page_post("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        call_args = self.mock_client.rget.call_args
        self.assertIn("params", call_args.kwargs)

    def test_get_status_page_post_unwrapped_response(self):
        """Test getting a Status Page Post with unwrapped response."""
        self.mock_client.rget.return_value = self.sample_post_data

        query = StatusPagePostQuery()
        result = get_status_page_post("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")

    def test_create_status_page_post_update_success(self):
        """Test creating a Status Page Post Update successfully."""
        self.mock_client.rpost.return_value = {"post_update": self.sample_post_update_data}

        update_request = StatusPagePostUpdateRequest(
            message="<p>Investigation ongoing</p>",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            impacted_services=[
                StatusPagePostUpdateImpact(
                    service=StatusPageServiceReference(id="PYHMEI3"),
                    impact=StatusPageImpactReference(id="PY5OM08"),
                )
            ],
            notify_subscribers=False,
            update_frequency_ms=300000,
            post=StatusPagePostReference(id="P6F2CJ3"),
        )

        wrapper = StatusPagePostUpdateRequestWrapper(post_update=update_request)
        result = create_status_page_post_update("PR5LMML", "P6F2CJ3", wrapper)

        self.assertIsInstance(result, StatusPagePostUpdate)
        self.assertEqual(result.id, "PXSOCH0")
        self.assertEqual(result.update_frequency_ms, 300000)
        self.mock_client.rpost.assert_called_once()

    def test_create_status_page_post_update_unwrapped_response(self):
        """Test creating a Status Page Post Update with unwrapped response."""
        self.mock_client.rpost.return_value = self.sample_post_update_data

        update_request = StatusPagePostUpdateRequest(
            message="<p>Investigation ongoing</p>",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            impacted_services=[],
            notify_subscribers=False,
            update_frequency_ms=300000,
            post=StatusPagePostReference(id="P6F2CJ3"),
        )

        wrapper = StatusPagePostUpdateRequestWrapper(post_update=update_request)
        result = create_status_page_post_update("PR5LMML", "P6F2CJ3", wrapper)

        self.assertIsInstance(result, StatusPagePostUpdate)
        self.assertEqual(result.id, "PXSOCH0")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_post_updates_basic(self, mock_paginate):
        """Test basic Post Update listing."""
        mock_paginate.return_value = [self.sample_post_update_data]

        query = StatusPagePostUpdateQuery()
        result = list_status_page_post_updates("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPagePostUpdate)
        self.assertEqual(result.response[0].id, "PXSOCH0")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_post_updates_filter_by_reviewed_status(self, mock_paginate):
        """Test Post Update listing with reviewed status filter."""
        mock_paginate.return_value = [self.sample_post_update_data]

        query = StatusPagePostUpdateQuery(reviewed_status="approved")
        result = list_status_page_post_updates("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].reviewed_status, "approved")

    def test_create_status_page_post_incident_with_required_fields(self):
        """Test creating an incident post with all required fields (starts_at, ends_at, updates)."""
        sample_incident_data = {
            "id": "PINC001",
            "self": "https://api.pagerduty.com/status_pages/P3E5S5D/posts/PINC001",
            "type": "status_page_post",
            "post_type": "incident",
            "status_page": {"id": "P3E5S5D", "type": "status_page"},
            "title": "Hotel Services Affected - Business Impact",
            "starts_at": "2023-12-12T11:00:00Z",
            "ends_at": "2023-12-12T12:00:00Z",
            "updates": [{"id": "PUPD001", "type": "status_page_post_update"}],
        }

        self.mock_client.rpost.return_value = {"post": sample_incident_data}

        update = StatusPagePostUpdateRequest(
            message="<p>Investigating the issue</p>",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            impacted_services=[],
            notify_subscribers=True,
            update_frequency_ms=300000,
        )

        post_request = StatusPagePostCreateRequest(
            title="Hotel Services Affected - Business Impact",
            post_type="incident",
            starts_at=datetime(2023, 12, 12, 11, 0, 0),
            ends_at=datetime(2023, 12, 12, 12, 0, 0),
            updates=[update],
            status_page=StatusPageReference(id="P3E5S5D"),
        )

        wrapper = StatusPagePostCreateRequestWrapper(post=post_request)
        result = create_status_page_post("P3E5S5D", wrapper)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PINC001")
        self.assertEqual(result.title, "Hotel Services Affected - Business Impact")
        self.assertEqual(result.post_type, "incident")
        self.mock_client.rpost.assert_called_once()

        call_args = self.mock_client.rpost.call_args
        json_data = call_args.kwargs["json"]
        self.assertEqual(json_data["post"]["title"], "Hotel Services Affected - Business Impact")
        self.assertEqual(json_data["post"]["post_type"], "incident")
        self.assertIn("updates", json_data["post"])
        self.assertIn("starts_at", json_data["post"])
        self.assertIn("ends_at", json_data["post"])
        self.assertIn("status_page", json_data["post"])

        # Verify datetime fields are serialized as strings (not datetime objects)
        self.assertIsInstance(json_data["post"]["starts_at"], str, "starts_at must be serialized as ISO string")
        self.assertIsInstance(json_data["post"]["ends_at"], str, "ends_at must be serialized as ISO string")
        self.assertEqual(json_data["post"]["starts_at"], "2023-12-12T11:00:00")
        self.assertEqual(json_data["post"]["ends_at"], "2023-12-12T12:00:00")

    def test_create_status_page_post_update_simple_message(self):
        """Test creating a post update with required fields and minimal optional fields."""
        self.mock_client.rpost.return_value = {"post_update": self.sample_post_update_data}

        update_request = StatusPagePostUpdateRequest(
            message="Work in progress",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            post=StatusPagePostReference(id="P6F2CJ3"),
        )

        wrapper = StatusPagePostUpdateRequestWrapper(post_update=update_request)
        result = create_status_page_post_update("PR5LMML", "P6F2CJ3", wrapper)

        self.assertIsInstance(result, StatusPagePostUpdate)
        self.assertEqual(result.id, "PXSOCH0")
        self.mock_client.rpost.assert_called_once()

        call_args = self.mock_client.rpost.call_args
        json_data = call_args.kwargs["json"]
        self.assertEqual(json_data["post_update"]["message"], "Work in progress")
        self.assertIn("status", json_data["post_update"])
        self.assertIn("severity", json_data["post_update"])
        self.assertEqual(json_data["post_update"]["notify_subscribers"], False)
        self.assertEqual(json_data["post_update"]["impacted_services"], [])

    def test_create_status_page_post_update_with_reported_at(self):
        """Test creating a post update with reported_at datetime field."""
        self.mock_client.rpost.return_value = {"post_update": self.sample_post_update_data}

        reported_time = datetime(2023, 12, 12, 14, 30, 0)
        update_request = StatusPagePostUpdateRequest(
            message="Issue has been resolved",
            status=StatusPageStatusReference(id="P0400H4"),
            severity=StatusPageSeverityReference(id="PY5OM08"),
            post=StatusPagePostReference(id="P6F2CJ3"),
            reported_at=reported_time,
        )

        wrapper = StatusPagePostUpdateRequestWrapper(post_update=update_request)
        result = create_status_page_post_update("PR5LMML", "P6F2CJ3", wrapper)

        self.assertIsInstance(result, StatusPagePostUpdate)
        self.mock_client.rpost.assert_called_once()

        call_args = self.mock_client.rpost.call_args
        json_data = call_args.kwargs["json"]
        self.assertIn("reported_at", json_data["post_update"])

        # Verify reported_at is serialized as string (not datetime object)
        self.assertIsInstance(
            json_data["post_update"]["reported_at"], str, "reported_at must be serialized as ISO string"
        )
        self.assertEqual(json_data["post_update"]["reported_at"], "2023-12-12T14:30:00")


if __name__ == "__main__":
    unittest.main()
