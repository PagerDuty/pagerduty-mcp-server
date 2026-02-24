

import unittest

from pagerduty_mcp.context import ContextResolver
from tests.mock_context_strategy import MockContextStrategy


class ContextTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_context = MockContextStrategy()
        self.mock_client = self.mock_context.client
        self.mock_user = self.mock_context.user

        ContextResolver.set_strategy(self.mock_context)

    def tearDown(self):
        ContextResolver._context_strategy = None
        return super().tearDown()
