"""Unit tests for alert grouping settings tools."""

import unittest
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models import (
    AlertGroupingSetting,
    AlertGroupingSettingCreate,
    AlertGroupingSettingCreateRequest,
    AlertGroupingSettingQuery,
    AlertGroupingSettingUpdateRequest,
    ContentBasedConfig,
    ContentBasedIntelligentConfig,
    IntelligentGroupingConfig,
    ListResponseModel,
    ServiceReference,
    TimeGroupingConfig,
)
from pagerduty_mcp.tools.alert_grouping_settings import (
    create_alert_grouping_setting,
    delete_alert_grouping_setting,
    get_alert_grouping_setting,
    list_alert_grouping_settings,
    update_alert_grouping_setting,
)


class TestAlertGroupingSettingsTools(unittest.TestCase):
    """Test cases for alert grouping settings tools."""

    @classmethod
    def setUpClass(cls):
        """Set up test data that will be reused across all test methods."""
        cls.sample_service_ref = {"id": "PSERVICE1", "summary": "Test Service", "type": "service_reference"}

        cls.sample_content_based_config = {
            "aggregate": "all",
            "fields": ["summary", "component", "custom_details.host"],
            "time_window": 900,
            "recommended_time_window": 1200,
        }

        cls.sample_time_config = {"timeout": 3600}

        cls.sample_intelligent_config = {
            "time_window": 1800,
            "recommended_time_window": 2100,
            "iag_fields": ["summary", "component"],
        }

        cls.sample_alert_grouping_setting = {
            "id": "PAGS123",
            "name": "Test Alert Grouping Setting",
            "description": "Test description for alert grouping",
            "type": "content_based",
            "config": cls.sample_content_based_config,
            "services": [cls.sample_service_ref],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

        cls.sample_time_based_setting = {
            "id": "PAGS456",
            "name": "Time Based Grouping",
            "description": "Time based alert grouping setting",
            "type": "time",
            "config": cls.sample_time_config,
            "services": [cls.sample_service_ref],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

        cls.sample_intelligent_setting = {
            "id": "PAGS789",
            "name": "Intelligent Grouping",
            "description": "Intelligent alert grouping setting",
            "type": "intelligent",
            "config": cls.sample_intelligent_config,
            "services": [cls.sample_service_ref],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

        cls.sample_list_response = [
            cls.sample_alert_grouping_setting,
            cls.sample_time_based_setting,
            cls.sample_intelligent_setting,
        ]

        cls.mock_client = MagicMock()

    def setUp(self):
        """Reset mock before each test."""
        self.mock_client.reset_mock()
        # Clear any side effects
        self.mock_client.rget.side_effect = None
        self.mock_client.rpost.side_effect = None
        self.mock_client.rput.side_effect = None
        self.mock_client.rdelete.side_effect = None

    @patch("pagerduty_mcp.tools.alert_grouping_settings.paginate")
    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_list_alert_grouping_settings_no_filters(self, mock_get_client, mock_paginate):
        """Test listing alert grouping settings without any filters."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_list_response

        query = AlertGroupingSettingQuery()
        result = list_alert_grouping_settings(query)

        # Verify paginate call
        mock_paginate.assert_called_once_with(
            client=self.mock_client,
            entity="alert_grouping_settings",
            params=query.to_params(),
            maximum_records=query.limit or 1000,
        )

        # Verify result
        self.assertIsInstance(result, ListResponseModel)
        self.assertEqual(len(result.response), 3)
        self.assertIsInstance(result.response[0], AlertGroupingSetting)
        self.assertIsInstance(result.response[1], AlertGroupingSetting)
        self.assertIsInstance(result.response[2], AlertGroupingSetting)
        self.assertEqual(result.response[0].id, "PAGS123")
        self.assertEqual(result.response[1].id, "PAGS456")
        self.assertEqual(result.response[2].id, "PAGS789")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.paginate")
    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_list_alert_grouping_settings_with_service_filter(self, mock_get_client, mock_paginate):
        """Test listing alert grouping settings with service filter."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = [self.sample_alert_grouping_setting]

        query = AlertGroupingSettingQuery(service_ids=["PSERVICE1"])
        result = list_alert_grouping_settings(query)

        # Verify paginate call with correct parameters
        mock_paginate.assert_called_once_with(
            client=self.mock_client,
            entity="alert_grouping_settings",
            params={"service_ids[]": ["PSERVICE1"], "limit": 20},
            maximum_records=20,
        )

        # Verify result
        self.assertEqual(len(result.response), 1)
        self.assertEqual(result.response[0].id, "PAGS123")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.paginate")
    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_list_alert_grouping_settings_with_limit(self, mock_get_client, mock_paginate):
        """Test listing alert grouping settings with custom limit."""
        mock_get_client.return_value = self.mock_client
        mock_paginate.return_value = self.sample_list_response[:2]

        query = AlertGroupingSettingQuery(limit=50)
        result = list_alert_grouping_settings(query)

        # Verify paginate call with custom limit
        mock_paginate.assert_called_once_with(
            client=self.mock_client, entity="alert_grouping_settings", params={"limit": 50}, maximum_records=50
        )

        # Verify result
        self.assertEqual(len(result.response), 2)

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_get_alert_grouping_setting_success(self, mock_get_client):
        """Test successful retrieval of a specific alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_alert_grouping_setting

        result = get_alert_grouping_setting("PAGS123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rget.assert_called_once_with("/alert_grouping_settings/PAGS123")

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS123")
        self.assertEqual(result.name, "Test Alert Grouping Setting")
        self.assertEqual(result.type, "content_based")
        self.assertIsInstance(result.config, ContentBasedConfig)
        self.assertEqual(result.config.aggregate, "all")
        self.assertEqual(result.config.time_window, 900)
        self.assertEqual(len(result.services), 1)
        self.assertEqual(result.services[0].id, "PSERVICE1")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_get_alert_grouping_setting_wrapped_response(self, mock_get_client):
        """Test retrieval with wrapped API response."""
        mock_get_client.return_value = self.mock_client
        wrapped_response = {"alert_grouping_setting": self.sample_alert_grouping_setting}
        self.mock_client.rget.return_value = wrapped_response

        result = get_alert_grouping_setting("PAGS123")

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS123")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_get_alert_grouping_setting_time_based(self, mock_get_client):
        """Test retrieval of time-based alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_time_based_setting

        result = get_alert_grouping_setting("PAGS456")

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS456")
        self.assertEqual(result.type, "time")
        self.assertIsInstance(result.config, TimeGroupingConfig)
        self.assertEqual(result.config.timeout, 3600)

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_get_alert_grouping_setting_intelligent(self, mock_get_client):
        """Test retrieval of intelligent alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rget.return_value = self.sample_intelligent_setting

        result = get_alert_grouping_setting("PAGS789")

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS789")
        self.assertEqual(result.type, "intelligent")
        self.assertIsInstance(result.config, IntelligentGroupingConfig)
        self.assertEqual(result.config.time_window, 1800)
        self.assertEqual(result.config.iag_fields, ["summary", "component"])

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_create_alert_grouping_setting_content_based(self, mock_get_client):
        """Test successful creation of content-based alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = self.sample_alert_grouping_setting

        # Create request
        config = ContentBasedConfig(aggregate="all", fields=["summary", "component"], time_window=900)
        service_ref = ServiceReference(id="PSERVICE1")
        setting = AlertGroupingSettingCreate(
            name="Test Alert Grouping Setting",
            description="Test description",
            type="content_based",
            config=config,
            services=[service_ref],
        )
        request = AlertGroupingSettingCreateRequest(alert_grouping_setting=setting)

        result = create_alert_grouping_setting(request)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rpost.assert_called_once_with(
            "/alert_grouping_settings", json=request.model_dump(exclude_none=True)
        )

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS123")
        self.assertEqual(result.name, "Test Alert Grouping Setting")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_create_alert_grouping_setting_wrapped_response(self, mock_get_client):
        """Test creation with wrapped API response."""
        mock_get_client.return_value = self.mock_client
        wrapped_response = {"alert_grouping_setting": self.sample_alert_grouping_setting}
        self.mock_client.rpost.return_value = wrapped_response

        # Create minimal request
        config = TimeGroupingConfig(timeout=3600)
        service_ref = ServiceReference(id="PSERVICE1")
        setting = AlertGroupingSettingCreate(
            name="Time Based Setting", type="time", config=config, services=[service_ref]
        )
        request = AlertGroupingSettingCreateRequest(alert_grouping_setting=setting)

        result = create_alert_grouping_setting(request)

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS123")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_create_alert_grouping_setting_intelligent(self, mock_get_client):
        """Test creation of intelligent alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rpost.return_value = self.sample_intelligent_setting

        # Create intelligent config
        config = IntelligentGroupingConfig(time_window=1800, iag_fields=["summary", "component"])
        service_ref = ServiceReference(id="PSERVICE1")
        setting = AlertGroupingSettingCreate(
            name="Intelligent Grouping", type="intelligent", config=config, services=[service_ref]
        )
        request = AlertGroupingSettingCreateRequest(alert_grouping_setting=setting)

        result = create_alert_grouping_setting(request)

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.type, "intelligent")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_update_alert_grouping_setting_success(self, mock_get_client):
        """Test successful update of alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        updated_setting = self.sample_alert_grouping_setting.copy()
        updated_setting["name"] = "Updated Alert Grouping Setting"
        self.mock_client.rput.return_value = updated_setting

        # Create update request
        config = ContentBasedConfig(aggregate="any", fields=["summary"], time_window=1800)
        service_ref = ServiceReference(id="PSERVICE1")
        setting = AlertGroupingSettingCreate(
            name="Updated Alert Grouping Setting", type="content_based", config=config, services=[service_ref]
        )
        request = AlertGroupingSettingUpdateRequest(alert_grouping_setting=setting)

        result = update_alert_grouping_setting("PAGS123", request)

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rput.assert_called_once_with(
            "/alert_grouping_settings/PAGS123", json=request.model_dump(exclude_none=True)
        )

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.name, "Updated Alert Grouping Setting")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_update_alert_grouping_setting_wrapped_response(self, mock_get_client):
        """Test update with wrapped API response."""
        mock_get_client.return_value = self.mock_client
        wrapped_response = {"alert_grouping_setting": self.sample_alert_grouping_setting}
        self.mock_client.rput.return_value = wrapped_response

        # Create minimal update request
        config = TimeGroupingConfig(timeout=7200)
        service_ref = ServiceReference(id="PSERVICE1")
        setting = AlertGroupingSettingCreate(
            name="Updated Time Setting", type="time", config=config, services=[service_ref]
        )
        request = AlertGroupingSettingUpdateRequest(alert_grouping_setting=setting)

        result = update_alert_grouping_setting("PAGS123", request)

        # Verify result
        self.assertIsInstance(result, AlertGroupingSetting)
        self.assertEqual(result.id, "PAGS123")

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_delete_alert_grouping_setting_success(self, mock_get_client):
        """Test successful deletion of alert grouping setting."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.return_value = None

        result = delete_alert_grouping_setting("PAGS123")

        # Verify API call
        mock_get_client.assert_called_once()
        self.mock_client.rdelete.assert_called_once_with("/alert_grouping_settings/PAGS123")

        # Verify result (should be None)
        self.assertIsNone(result)

    @patch("pagerduty_mcp.tools.alert_grouping_settings.get_client")
    def test_delete_alert_grouping_setting_client_error(self, mock_get_client):
        """Test delete when client raises an exception."""
        mock_get_client.return_value = self.mock_client
        self.mock_client.rdelete.side_effect = Exception("API Error")

        with self.assertRaises(Exception) as context:
            delete_alert_grouping_setting("PAGS123")

        self.assertEqual(str(context.exception), "API Error")
        mock_get_client.assert_called_once()
        self.mock_client.rdelete.assert_called_once_with("/alert_grouping_settings/PAGS123")

    def test_alert_grouping_setting_query_to_params(self):
        """Test AlertGroupingSettingQuery.to_params() method."""
        # Test empty query
        query = AlertGroupingSettingQuery()
        params = query.to_params()
        self.assertEqual(params, {"limit": 20})

        # Test query with all parameters
        query = AlertGroupingSettingQuery(
            service_ids=["PSERVICE1", "PSERVICE2"], limit=50, after="cursor_after", before="cursor_before", total=True
        )
        params = query.to_params()
        expected = {
            "service_ids[]": ["PSERVICE1", "PSERVICE2"],
            "limit": 50,
            "after": "cursor_after",
            "before": "cursor_before",
            "total": True,
        }
        self.assertEqual(params, expected)

        # Test query with service_ids only
        query = AlertGroupingSettingQuery(service_ids=["PSERVICE1"])
        params = query.to_params()
        expected = {"service_ids[]": ["PSERVICE1"], "limit": 20}
        self.assertEqual(params, expected)

    def test_content_based_intelligent_config_validation(self):
        """Test ContentBasedIntelligentConfig validation constraints."""
        # Test valid config
        config = ContentBasedIntelligentConfig(
            aggregate="all",
            fields=["summary"],
            time_window=3600,  # Max allowed for intelligent
        )
        self.assertEqual(config.time_window, 3600)

        # Test invalid time_window (too high for intelligent)
        with self.assertRaises(ValueError):
            ContentBasedIntelligentConfig(
                aggregate="all",
                fields=["summary"],
                time_window=86400,  # Too high for content_based_intelligent
            )

    def test_time_grouping_config_validation(self):
        """Test TimeGroupingConfig validation constraints."""
        # Test valid config
        config = TimeGroupingConfig(timeout=3600)
        self.assertEqual(config.timeout, 3600)

        # Test minimum value
        config = TimeGroupingConfig(timeout=60)
        self.assertEqual(config.timeout, 60)

        # Test invalid timeout (too low)
        with self.assertRaises(ValueError):
            TimeGroupingConfig(timeout=30)  # Below minimum

        # Test invalid timeout (too high)
        with self.assertRaises(ValueError):
            TimeGroupingConfig(timeout=100000)  # Above maximum


if __name__ == "__main__":
    unittest.main()
