from pagerduty import RestApiV2Client
from pagerduty.errors import HttpError

from pagerduty_mcp.models import MAX_RESULTS, MCPContext, User


def get_mcp_context(client: RestApiV2Client) -> MCPContext:
    """Get MCP Context.

    This function takes the user credentials and determines if this is an account or user level
    auth mode.

    If the credentials are bound to a user, it will return the user Schema. Otherwise None.
    """
    try:
        response = client.rget("/users/me")
        # add the from header so all requests are made from the user
        if type(response) is dict:
            user_email = response.get("email", "no-email-provided")
            client.headers["From"] = user_email
        return MCPContext(user=User.model_validate(response))

    except HttpError:
        return MCPContext(user=None)


def paginate(*, client: RestApiV2Client, entity: str, params: dict, maximum_records: int = MAX_RESULTS):
    """Paginate results.

    Paginate through the results of a request to the PagerDuty API, while allowing for early termination
    if the maximum number of records is reached.

    Args:
        client: The PagerDuty API client
        entity: The entity to paginate through (e.g., "incidents")
        params: The parameters to pass to the API request
        maximum_records: The maximum number of records to return
    Returns:
        A list of results
    """
    results = []
    count = 0
    for incident in client.iter_all(entity, params=params):
        results.append(incident)
        count += 1  # noqa: SIM113
        if count >= maximum_records:
            break
    return results
