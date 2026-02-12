import logging
import os
from importlib import metadata

from dotenv import load_dotenv
from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp import DIST_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("PAGERDUTY_USER_API_KEY")
API_HOST = os.getenv("PAGERDUTY_API_HOST", "https://api.pagerduty.com")


class PagerdutyMCPClient(RestApiV2Client):
    @property
    def user_agent(self) -> str:
        return f"{DIST_NAME}/{metadata.version(DIST_NAME)} {super().user_agent}"


def get_client() -> RestApiV2Client:
    """Get the PagerDuty client using environment variables.

    This function is kept for backward compatibility but should be deprecated
    in favor of dependency injection through application context.
    """
    pd_client = PagerdutyMCPClient(API_KEY)
    if API_HOST:
        pd_client.url = API_HOST
    return pd_client

