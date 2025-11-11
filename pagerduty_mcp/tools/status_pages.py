from pagerduty_mcp.client import get_client
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
        entity="severities",
        params=params,
        maximum_records=query_model.limit or 100,
        base_url=f"/status_pages/{status_page_id}",
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
        entity="impacts",
        params=params,
        maximum_records=query_model.limit or 100,
        base_url=f"/status_pages/{status_page_id}",
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
        entity="statuses",
        params=params,
        maximum_records=query_model.limit or 100,
        base_url=f"/status_pages/{status_page_id}",
    )

    statuses = [StatusPageStatus(**item) for item in response]
    return ListResponseModel[StatusPageStatus](response=statuses)


def create_status_page_post(status_page_id: str, create_model: StatusPagePostCreateRequestWrapper) -> StatusPagePost:
    """Create a Post for a Status Page by Status Page ID.

    This tool creates a new post (incident or maintenance) on a status page.
    For maintenance posts, you can specify a simple post with just title, post_type,
    starts_at, and ends_at. Updates can be added later using create_status_page_post_update.

    Args:
        status_page_id: The ID of the Status Page
        create_model: The post creation request. At minimum, must include:
            - post.title: The title of the post
            - post.post_type: Either "incident" or "maintenance"
            - post.starts_at: Start time (for maintenance posts)
            - post.ends_at: End time (for maintenance posts)

    Returns:
        The created StatusPagePost
    """
    response = get_client().rpost(
        f"/status_pages/{status_page_id}/posts", json=create_model.model_dump(exclude_none=True)
    )

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

    This tool adds a new update to an existing status page post. You can create
    simple text updates with just a message, or more detailed updates that include
    status, severity, and impacted services information.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        create_model: The post update creation request. At minimum, must include:
            - post_update.message: The message text for the update
            Optional fields for detailed updates:
            - post_update.status: Status reference (e.g., "investigating", "resolved")
            - post_update.severity: Severity reference (e.g., "minor", "major")
            - post_update.impacted_services: List of impacted services and their impact levels

    Returns:
        The created StatusPagePostUpdate
    """
    response = get_client().rpost(
        f"/status_pages/{status_page_id}/posts/{post_id}/post_updates",
        json=create_model.model_dump(exclude_none=True),
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
        entity="post_updates",
        params=params,
        maximum_records=query_model.limit or 100,
        base_url=f"/status_pages/{status_page_id}/posts/{post_id}",
    )

    post_updates = [StatusPagePostUpdate(**item) for item in response]
    return ListResponseModel[StatusPagePostUpdate](response=post_updates)
