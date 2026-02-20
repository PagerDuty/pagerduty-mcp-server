from pagerduty_mcp.context import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.status_pages import (
    StatusPage,
    StatusPageImpact,
    StatusPageImpactQuery,
    StatusPagePost,
    StatusPagePostCreateRequestWrapper,
    StatusPagePostQuery,
    StatusPagePostUpdate,
    StatusPagePostUpdateQuery,
    StatusPagePostUpdateRequestWrapper,
    StatusPageQuery,
    StatusPageSeverity,
    StatusPageSeverityQuery,
    StatusPageStatus,
    StatusPageStatusQuery,
)
from pagerduty_mcp.utils import paginate


def list_status_pages(query_model: StatusPageQuery) -> ListResponseModel[StatusPage]:
    """List Status Pages with optional filtering.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of StatusPage objects matching the query parameters
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity="status_pages",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    status_pages = [StatusPage(**item) for item in response]
    return ListResponseModel[StatusPage](response=status_pages)


def list_status_page_severities(
    status_page_id: str, query_model: StatusPageSeverityQuery
) -> ListResponseModel[StatusPageSeverity]:
    """List Severities for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        query_model: Optional filtering parameters

    Returns:
        List of StatusPageSeverity objects for the given Status Page
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/severities",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    severities = [StatusPageSeverity(**item) for item in response]
    return ListResponseModel[StatusPageSeverity](response=severities)


def list_status_page_impacts(
    status_page_id: str, query_model: StatusPageImpactQuery
) -> ListResponseModel[StatusPageImpact]:
    """List Impacts for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        query_model: Optional filtering parameters

    Returns:
        List of StatusPageImpact objects for the given Status Page
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/impacts",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    impacts = [StatusPageImpact(**item) for item in response]
    return ListResponseModel[StatusPageImpact](response=impacts)


def list_status_page_statuses(
    status_page_id: str, query_model: StatusPageStatusQuery
) -> ListResponseModel[StatusPageStatus]:
    """List Statuses for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        query_model: Optional filtering parameters

    Returns:
        List of StatusPageStatus objects for the given Status Page
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/statuses",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    statuses = [StatusPageStatus(**item) for item in response]
    return ListResponseModel[StatusPageStatus](response=statuses)


def create_status_page_post(status_page_id: str, create_model: StatusPagePostCreateRequestWrapper) -> StatusPagePost:
    """Create a Post for a Status Page by Status Page ID.

    This tool creates a new post (incident or maintenance) on a status page.
    According to the PagerDuty API, all posts require starts_at, ends_at, and at least one update.

    Args:
        status_page_id: The ID of the Status Page
        create_model: The post creation request. Must include:
            - post.title: The title of the post
            - post.post_type: Either "incident" or "maintenance"
            - post.starts_at: When the post becomes effective (required)
            - post.ends_at: When the post is concluded (required)
            - post.updates: List of at least one post update with message, status, severity, etc.

    Returns:
        The created StatusPagePost
    """
    response = get_client().rpost(f"/status_pages/{status_page_id}/posts", json=create_model.model_dump(mode="json"))

    return StatusPagePost.from_api_response(response)


def get_status_page_post(status_page_id: str, post_id: str, query_model: StatusPagePostQuery) -> StatusPagePost:
    """Get a Post for a Status Page by Status Page ID and Post ID.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        query_model: Optional query parameters (e.g., include related resources)

    Returns:
        StatusPagePost details
    """
    params = query_model.to_params()
    response = get_client().rget(f"/status_pages/{status_page_id}/posts/{post_id}", params=params)

    return StatusPagePost.from_api_response(response)


def create_status_page_post_update(
    status_page_id: str, post_id: str, create_model: StatusPagePostUpdateRequestWrapper
) -> StatusPagePostUpdate:
    """Create a Post Update for a Post by Post ID.

    This tool adds a new update to an existing status page post.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        create_model: The post update creation request. Must include:
            - post_update.message: The message text for the update
            - post_update.status: Status reference (required)
            - post_update.severity: Severity reference (required)
            - post_update.post: Post reference (required)
            Optional fields with defaults:
            - post_update.impacted_services: List of impacted services (defaults to empty list)
            - post_update.notify_subscribers: Whether to notify subscribers (defaults to False)
            - post_update.update_frequency_ms: Update frequency in milliseconds (defaults to null)

    Returns:
        The created StatusPagePostUpdate
    """
    response = get_client().rpost(
        f"/status_pages/{status_page_id}/posts/{post_id}/post_updates",
        json=create_model.model_dump(mode="json"),
    )

    return StatusPagePostUpdate.from_api_response(response)


def list_status_page_post_updates(
    status_page_id: str, post_id: str, query_model: StatusPagePostUpdateQuery
) -> ListResponseModel[StatusPagePostUpdate]:
    """List Post Updates for a Status Page by Status Page ID and Post ID.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        query_model: Optional filtering parameters

    Returns:
        List of StatusPagePostUpdate objects for the given Post
    """
    params = query_model.to_params()

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/posts/{post_id}/post_updates",
        params=params,
        maximum_records=query_model.limit or 100,
    )

    post_updates = [StatusPagePostUpdate(**item) for item in response]
    return ListResponseModel[StatusPagePostUpdate](response=post_updates)
