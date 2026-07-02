from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.references import PriorityReference
from pagerduty_mcp.utils import paginate


def list_priorities() -> str:
    """List all priorities configured in the account.

    Returns:
        JSON string of ListResponseModel containing PriorityReference objects
    """
    response = paginate(
        client=get_client(),
        entity="priorities",
        params={},
        maximum_records=100,
    )

    priorities = [PriorityReference(**priority) for priority in response]
    return ListResponseModel[PriorityReference](response=priorities).model_dump_json()
