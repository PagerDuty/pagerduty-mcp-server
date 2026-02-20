from pagerduty import RestApiV2Client
from pagerduty_mcp.models import MAX_RESULTS


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
