import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models import (
    StatusPage,
    StatusPageImpact,
    StatusPageImpactQuery,
    StatusPagePost,
    StatusPagePostCreate,
    StatusPagePostCreateRequest,
    StatusPagePostUpdate,
    StatusPagePostUpdateRequest,
    StatusPagePostUpdateRequestBody,
    StatusPageQuery,
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


class TestStatusPageTools(unittest.TestCase):
    """Test cases for status page tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_status_page = {
            "id": "PT4KHLK",
            "name": "My brand Status Page",
            "published_at": "2017-09-13T10:11:12Z",
            "status_page_type": "private",
            "type": "status_page",
            "url": "https://status.mybrand.example",
        }

        cls.sample_status_pages_list = [
            {
                "id": "PT4KHLK",
                "name": "My brand Status Page",
                "published_at": "2017-09-13T10:11:12Z",
                "status_page_type": "private",
                "type": "status_page",
                "url": "https://status.mybrand.example",
            },
            {
                "id": "PT5KHLK",
                "name": "Public Status Page",
                "published_at": "2017-09-14T10:11:12Z",
                "status_page_type": "public",
                "type": "status_page",
                "url": "https://status.public.example",
            },
        ]

        cls.sample_severity = {
            "description": "all good",
            "id": "PIJ90N7",
            "post_type": "incident",
            "self": "https://api.pagerduty.com/status_pages/PQ8W0D0/severities/PIJ90N7",
            "status_page": {"id": "PQ8W0D0", "type": "status_page"},
            "type": "status_page_severity",
        }

        cls.sample_severities_list = [
            {
                "description": "all good",
                "id": "PIJ90N7",
                "post_type": "incident",
                "self": "https://api.pagerduty.com/status_pages/PQ8W0D0/severities/PIJ90N7",
                "status_page": {"id": "PQ8W0D0", "type": "status_page"},
                "type": "status_page_severity",
            },
            {
                "description": "minor",
                "id": "PF9KMXH",
                "post_type": "incident",
                "self": "https://api.pagerduty.com/status_pages/PQ8W0D0/severities/PF9KMXH",
                "status_page": {"id": "PQ8W0D0", "type": "status_page"},
                "type": "status_page_severity",
            },
        ]

        cls.sample_impact = {
            "description": "minor degradation",
            "id": "PY5OM08",
            "post_type": "incident",
            "self": "https://api.pagerduty.com/status_pages/PR5LMML/impacts/PY5OM08",
            "status_page": {"id": "PR5LMML", "type": "status_page"},
            "type": "status_page_impact",
        }

        cls.sample_impacts_list = [
            {
                "description": "minor degradation",
                "id": "PY5OM08",
                "post_type": "incident",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/impacts/PY5OM08",
                "status_page": {"id": "PR5LMML", "type": "status_page"},
                "type": "status_page_impact",
            },
            {
                "description": "major outage",
                "id": "PZ5OM09",
                "post_type": "incident",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/impacts/PZ5OM09",
                "status_page": {"id": "PR5LMML", "type": "status_page"},
                "type": "status_page_impact",
            },
        ]

        cls.sample_status = {
            "description": "investigating",
            "id": "P0400H4",
            "post_type": "incident",
            "self": "https://api.pagerduty.com/status_pages/PR5LMML/statuses/P0400H4",
            "status_page": {"id": "PR5LMML", "type": "status_page"},
            "type": "status_page_status",
        }

        cls.sample_statuses_list = [
            {
                "description": "investigating",
                "id": "P0400H4",
                "post_type": "incident",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/statuses/P0400H4",
                "status_page": {"id": "PR5LMML", "type": "status_page"},
                "type": "status_page_status",
            },
            {
                "description": "resolved",
                "id": "P0400H5",
                "post_type": "incident",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/statuses/P0400H5",
                "status_page": {"id": "PR5LMML", "type": "status_page"},
                "type": "status_page_status",
            },
        ]

        cls.sample_post = {
            "ends_at": "2023-12-12T11:00:00Z",
            "id": "PIJ90N7",
            "post_type": "maintenance",
            "postmortem": {
                "id": "PWZ0PTR",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/PIJ90N7/postmortem",
                "type": "status_page_postmortem",
            },
            "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/PIJ90N7",
            "starts_at": "2023-12-12T11:00:00Z",
            "status_page": {"id": "PR5LMML", "type": "status_page"},
            "title": "maintenance window for database upgrade",
            "type": "status_page_post",
            "updates": [
                {
                    "id": "P7HUBBZ",
                    "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/PIJ90N7/post_updates/P7HUBBZ",
                    "type": "status_page_post_update",
                }
            ],
        }

        cls.sample_post_update = {
            "id": "PXSOCH0",
            "impacted_services": [
                {
                    "impact": {
                        "id": "PY5OM08",
                        "self": "https://api.pagerduty.com/status_pages/PR5LMML/impacts/PY5OM08",
                        "type": "status_page_impact",
                    },
                    "service": {
                        "id": "PYHMEI3",
                        "self": "https://api.pagerduty.com/status_pages/PR5LMML/services/PYHMEI3",
                        "type": "status_page_service",
                    },
                }
            ],
            "message": "<p>We will be undergoing schedule maitenance at this date and time</p>",
            "notify_subscribers": False,
            "post": {
                "id": "P6F2CJ3",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/P6F2CJ3",
                "type": "status_page_post",
            },
            "reported_at": "2023-12-12T10:08:19Z",
            "reviewed_status": "approved",
            "self": "https://api.pagerduty.com/status_pages/PR5LMML/posts/P6F2CJ3/post_updates/PXSOCH0",
            "severity": {
                "id": "PY5OM08",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/severities/PY5OM08",
                "type": "status_page_severity",
            },
            "status": {
                "id": "P0400H4",
                "self": "https://api.pagerduty.com/status_pages/PR5LMML/statuses/P0400H4",
                "type": "status_page_status",
            },
            "type": "status_page_post_update",
        }

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None
        self.mock_client.rput.side_effect = None
        self.mock_client.rdelete.side_effect = None

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_pages_success(self, mock_get_client, mock_paginate):
        """Test successful listing of status pages."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_status_pages_list

        query = StatusPageQuery()
        result = list_status_pages(query)

        mock_paginate.assert_called_once_with(client=self.mock_client, entity="status_pages", params={})

        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], StatusPage)
        self.assertIsInstance(result.response[1], StatusPage)
        self.assertEqual(result.response[0].id, "PT4KHLK")
        self.assertEqual(result.response[1].id, "PT5KHLK")
        self.assertEqual(result.response[0].status_page_type, "private")
        self.assertEqual(result.response[1].status_page_type, "public")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_pages_with_type_filter(self, mock_get_client, mock_paginate):
        """Test listing status pages with type filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_status_pages_list[0]]

        query = StatusPageQuery(status_page_type="private")
        result = list_status_pages(query)

        expected_params = {"status_page_type": "private"}
        mock_paginate.assert_called_once_with(client=self.mock_client, entity="status_pages", params=expected_params)

        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].status_page_type, "private")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_severities_success(self, mock_get_client, mock_paginate):
        """Test successful listing of severities."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_severities_list

        query = StatusPageSeverityQuery()
        result = list_status_page_severities("PQ8W0D0", query)

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PQ8W0D0/severities", params={}
        )

        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], StatusPageSeverity)
        self.assertIsInstance(result.response[1], StatusPageSeverity)
        self.assertEqual(result.response[0].id, "PIJ90N7")
        self.assertEqual(result.response[1].id, "PF9KMXH")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_severities_with_post_type(self, mock_get_client, mock_paginate):
        """Test listing severities with post type filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_severities_list

        query = StatusPageSeverityQuery(post_type="incident")
        result = list_status_page_severities("PQ8W0D0", query)

        expected_params = {"post_type": "incident"}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PQ8W0D0/severities", params=expected_params
        )

        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_impacts_success(self, mock_get_client, mock_paginate):
        """Test successful listing of impacts."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_impacts_list

        query = StatusPageImpactQuery()
        result = list_status_page_impacts("PR5LMML", query)

        mock_paginate.assert_called_once_with(client=self.mock_client, entity="status_pages/PR5LMML/impacts", params={})

        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], StatusPageImpact)
        self.assertIsInstance(result.response[1], StatusPageImpact)
        self.assertEqual(result.response[0].id, "PY5OM08")
        self.assertEqual(result.response[1].id, "PZ5OM09")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_impacts_with_post_type(self, mock_get_client, mock_paginate):
        """Test listing impacts with post type filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_impacts_list

        query = StatusPageImpactQuery(post_type="maintenance")
        result = list_status_page_impacts("PR5LMML", query)

        expected_params = {"post_type": "maintenance"}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PR5LMML/impacts", params=expected_params
        )

        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_statuses_success(self, mock_get_client, mock_paginate):
        """Test successful listing of statuses."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_statuses_list

        query = StatusPageStatusQuery()
        result = list_status_page_statuses("PR5LMML", query)

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PR5LMML/statuses", params={}
        )

        self.assertEqual(len(result.response), 2)
        self.assertIsInstance(result.response[0], StatusPageStatus)
        self.assertIsInstance(result.response[1], StatusPageStatus)
        self.assertEqual(result.response[0].id, "P0400H4")
        self.assertEqual(result.response[1].id, "P0400H5")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_statuses_with_post_type(self, mock_get_client, mock_paginate):
        """Test listing statuses with post type filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_statuses_list

        query = StatusPageStatusQuery(post_type="incident")
        result = list_status_page_statuses("PR5LMML", query)

        expected_params = {"post_type": "incident"}
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PR5LMML/statuses", params=expected_params
        )

        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_wrapped_response(self, mock_get_client):
        """Test creating a post with wrapped response."""
        mock_get_client.return_value = self.mock_client
        wrapped_response = {"post": self.sample_post}
        self.mock_client.rpost.return_value = wrapped_response

        post_data = StatusPagePostCreate(
            title="Scheduled Maintenance", post_type="maintenance", starts_at=datetime(2023, 12, 12, 11, 0, 0)
        )
        request = StatusPagePostCreateRequest(post=post_data)

        result = create_status_page_post("PR5LMML", request)

        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once()

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_direct_response(self, mock_get_client):
        """Test creating a post with direct response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = self.sample_post

        post_data = StatusPagePostCreate(
            title="Scheduled Maintenance", post_type="maintenance", starts_at=datetime(2023, 12, 12, 11, 0, 0)
        )
        request = StatusPagePostCreateRequest(post=post_data)

        result = create_status_page_post("PR5LMML", request)

        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once()

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_get_status_page_post_wrapped_response(self, mock_get_client):
        """Test getting a post with wrapped response."""
        mock_get_client.return_value = self.mock_client
        wrapped_response = {"post": self.sample_post}
        self.mock_client.rget.return_value = wrapped_response

        result = get_status_page_post("PR5LMML", "PIJ90N7")

        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/status_pages/PR5LMML/posts/PIJ90N7")

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_get_status_page_post_direct_response(self, mock_get_client):
        """Test getting a post with direct response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_post

        result = get_status_page_post("PR5LMML", "PIJ90N7")

        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/status_pages/PR5LMML/posts/PIJ90N7")

        self.assertIsInstance(result, StatusPagePost)
        self.assertEqual(result.id, "PIJ90N7")
        self.assertEqual(result.title, "maintenance window for database upgrade")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_update_wrapped_response(self, mock_get_client):
        """Test creating a post update with wrapped response."""
        mock_get_client.return_value = self.mock_client
        wrapped_response = {"post_update": self.sample_post_update}
        self.mock_client.rpost.return_value = wrapped_response

        update = StatusPagePostUpdateRequest(
            message="Issue has been resolved",
            severity=StatusPageSeverityReference(id="PY5OM08"),
            status=StatusPageStatusReference(id="P0400H4"),
        )
        request = StatusPagePostUpdateRequestBody(post_update=update)

        result = create_status_page_post_update("PR5LMML", "P6F2CJ3", request)

        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once()

        self.assertIsInstance(result, StatusPagePostUpdate)
        self.assertEqual(result.id, "PXSOCH0")

    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_create_status_page_post_update_direct_response(self, mock_get_client):
        """Test creating a post update with direct response."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = self.sample_post_update

        update = StatusPagePostUpdateRequest(
            message="Issue has been resolved",
            severity=StatusPageSeverityReference(id="PY5OM08"),
            status=StatusPageStatusReference(id="P0400H4"),
        )
        request = StatusPagePostUpdateRequestBody(post_update=update)

        result = create_status_page_post_update("PR5LMML", "P6F2CJ3", request)

        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once()

        self.assertIsInstance(result, StatusPagePostUpdate)
        self.assertEqual(result.id, "PXSOCH0")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_post_updates_success(self, mock_get_client, mock_paginate):
        """Test successful listing of post updates."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_post_update]

        result = list_status_page_post_updates("PR5LMML", "P6F2CJ3")

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PR5LMML/posts/P6F2CJ3/post_updates", params={}
        )

        self.assertEqual(len(result.response), 1)
        self.assertIsInstance(result.response[0], StatusPagePostUpdate)
        self.assertEqual(result.response[0].id, "PXSOCH0")

    @patch("pagerduty_mcp.tools.status_pages.paginate")
    @patch("pagerduty_mcp.tools.status_pages.get_client")
    def test_list_status_page_post_updates_empty(self, mock_get_client, mock_paginate):
        """Test listing post updates when there are none."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = []

        result = list_status_page_post_updates("PR5LMML", "P6F2CJ3")

        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="status_pages/PR5LMML/posts/P6F2CJ3/post_updates", params={}
        )

        self.assertEqual(len(result.response), 0)

    def test_status_page_query_to_params_with_type(self):
        """Test StatusPageQuery.to_params() with type filter."""
        query = StatusPageQuery(status_page_type="public")
        params = query.to_params()
        expected_params = {"status_page_type": "public"}
        self.assertEqual(params, expected_params)

    def test_status_page_query_to_params_empty(self):
        """Test StatusPageQuery.to_params() with no filters."""
        query = StatusPageQuery()
        params = query.to_params()
        expected_params = {}
        self.assertEqual(params, expected_params)

    def test_severity_query_to_params_with_post_type(self):
        """Test StatusPageSeverityQuery.to_params() with post type filter."""
        query = StatusPageSeverityQuery(post_type="incident")
        params = query.to_params()
        expected_params = {"post_type": "incident"}
        self.assertEqual(params, expected_params)

    def test_severity_query_to_params_empty(self):
        """Test StatusPageSeverityQuery.to_params() with no filters."""
        query = StatusPageSeverityQuery()
        params = query.to_params()
        expected_params = {}
        self.assertEqual(params, expected_params)


if __name__ == "__main__":
    unittest.main()
