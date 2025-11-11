"""Unit tests for Status Pages tools."""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

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


class TestStatusPagesTools(unittest.TestCase):
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

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_pages_basic(self, mock_paginate, mock_get_client):
        """Test basic Status Pages listing."""
        mock_paginate.return_value = [self.sample_status_page_data]

        query = StatusPageQuery()
        result = list_status_pages(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPage)
        self.assertEqual(result.response[0].id, "PT4KHLK")
        self.assertEqual(result.response[0].name, "My brand Status Page")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_pages_filter_by_type(self, mock_paginate, mock_get_client):
        """Test Status Pages listing with type filter."""
        mock_paginate.return_value = [self.sample_status_page_data]

        query = StatusPageQuery(status_page_type="private")
        result = list_status_pages(query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].status_page_type, "private")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_severities_basic(self, mock_paginate, mock_get_client):
        """Test basic Severity listing."""
        mock_paginate.return_value = [self.sample_severity_data]

        query = StatusPageSeverityQuery()
        result = list_status_page_severities("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPageSeverity)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[0].description, "all good")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_severities_filter_by_post_type(self, mock_paginate, mock_get_client):
        """Test Severity listing with post type filter."""
        mock_paginate.return_value = [self.sample_severity_data]

        query = StatusPageSeverityQuery(post_type="incident")
        result = list_status_page_severities("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].post_type, "incident")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_impacts_basic(self, mock_paginate, mock_get_client):
        """Test basic Impact listing."""
        mock_paginate.return_value = [self.sample_impact_data]

        query = StatusPageImpactQuery()
        result = list_status_page_impacts("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPageImpact)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[0].description, "operational")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_impacts_filter_by_post_type(self, mock_paginate, mock_get_client):
        """Test Impact listing with post type filter."""
        mock_paginate.return_value = [self.sample_impact_data]

        query = StatusPageImpactQuery(post_type="incident")
        result = list_status_page_impacts("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].post_type, "incident")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_statuses_basic(self, mock_paginate, mock_get_client):
        """Test basic Status listing."""
        mock_paginate.return_value = [self.sample_status_data]

        query = StatusPageStatusQuery()
        result = list_status_page_statuses("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPageStatus)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[0].description, "investigating")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_statuses_filter_by_post_type(self, mock_paginate, mock_get_client):
        """Test Status listing with post type filter."""
        mock_paginate.return_value = [self.sample_status_data]

        query = StatusPageStatusQuery(post_type="incident")
        result = list_status_page_statuses("PQ8W0D0", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].post_type, "incident")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_success(self, mock_get_client):
        """Test creating a Status Page Post successfully."""
        mock_client = Mock()
        mock_client.rpost.return_value = {"post": self.sample_post_data}
        mock_get_client.return_value = mock_client

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
        mock_client.rpost.assert_called_once()

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_unwrapped_response(self, mock_get_client):
        """Test creating a Status Page Post with unwrapped response."""
        mock_client = Mock()
        mock_client.rpost.return_value = self.sample_post_data
        mock_get_client.return_value = mock_client

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

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_get_status_page_post_success(self, mock_get_client):
        """Test getting a Status Page Post successfully."""
        mock_client = Mock()
        mock_client.rget.return_value = {"post": self.sample_post_data}
        mock_get_client.return_value = mock_client

        query = StatusPagePostQuery()
        result = get_status_page_post("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")
        mock_client.rget.assert_called_once()

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_get_status_page_post_with_includes(self, mock_get_client):
        """Test getting a Status Page Post with included resources."""
        mock_client = Mock()
        mock_client.rget.return_value = {"post": self.sample_post_data}
        mock_get_client.return_value = mock_client

        query = StatusPagePostQuery(include=["status_page_post_update"])
        result = get_status_page_post("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        call_args = mock_client.rget.call_args
        self.assertIn("params", call_args.kwargs)

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_get_status_page_post_unwrapped_response(self, mock_get_client):
        """Test getting a Status Page Post with unwrapped response."""
        mock_client = Mock()
        mock_client.rget.return_value = self.sample_post_data
        mock_get_client.return_value = mock_client

        query = StatusPagePostQuery()
        result = get_status_page_post("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_update_success(self, mock_get_client):
        """Test creating a Status Page Post Update successfully."""
        mock_client = Mock()
        mock_client.rpost.return_value = {"post_update": self.sample_post_update_data}
        mock_get_client.return_value = mock_client

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
        mock_client.rpost.assert_called_once()

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_update_unwrapped_response(self, mock_get_client):
        """Test creating a Status Page Post Update with unwrapped response."""
        mock_client = Mock()
        mock_client.rpost.return_value = self.sample_post_update_data
        mock_get_client.return_value = mock_client

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

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_post_updates_basic(self, mock_paginate, mock_get_client):
        """Test basic Post Update listing."""
        mock_paginate.return_value = [self.sample_post_update_data]

        query = StatusPagePostUpdateQuery()
        result = list_status_page_post_updates("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPagePostUpdate)
        self.assertEqual(result.response[0].id, "PXSOCH0")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    @patch("pagerduty_mcp.tools.status_pages.paginate")
    def test_list_status_page_post_updates_filter_by_reviewed_status(self, mock_paginate, mock_get_client):
        """Test Post Update listing with reviewed status filter."""
        mock_paginate.return_value = [self.sample_post_update_data]

        query = StatusPagePostUpdateQuery(reviewed_status="approved")
        result = list_status_page_post_updates("PR5LMML", "PIJ90N7", query)

        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].reviewed_status, "approved")


if __name__ == "__main__":
    unittest.main()
