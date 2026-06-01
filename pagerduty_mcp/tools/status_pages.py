import json
from typing import Any, Literal

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel
from pagerduty_mcp.models.base import DEFAULT_PAGINATION_LIMIT
from pagerduty_mcp.models.status_pages import (
    StatusPage,
    StatusPageImpact,
    StatusPagePost,
    StatusPagePostCreateRequestWrapper,
    StatusPagePostUpdate,
    StatusPagePostUpdateRequestWrapper,
    StatusPageSeverity,
    StatusPageStatus,
)
from pagerduty_mcp.utils import paginate


def list_status_pages(
    status_page_type: Literal["public", "private", "audience_specific"] | None = None,
    limit: int | None = DEFAULT_PAGINATION_LIMIT,
) -> ListResponseModel[StatusPage]:
    """List Status Pages with optional filtering.

    Args:
        status_page_type: Filter by the type of the Status Page.
            Options: 'public', 'private', 'audience_specific'.
        limit: Maximum number of results to return. Default 20.

    Returns:
        List of StatusPage objects
    """
    params: dict[str, Any] = {}
    if status_page_type:
        params["status_page_type"] = status_page_type
    if limit:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity="status_pages",
        params=params,
        maximum_records=limit or DEFAULT_PAGINATION_LIMIT,
    )

    status_pages = [StatusPage(**item) for item in response]
    return ListResponseModel[StatusPage](response=status_pages)


def list_status_page_severities(
    status_page_id: str,
    post_type: Literal["incident", "maintenance"] | None = None,
    limit: int | None = DEFAULT_PAGINATION_LIMIT,
) -> ListResponseModel[StatusPageSeverity]:
    """List Severities for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        post_type: Filter by post type: 'incident' or 'maintenance'.
        limit: Maximum number of results to return. Default 20.

    Returns:
        List of StatusPageSeverity objects for the given Status Page
    """
    params: dict[str, Any] = {}
    if post_type:
        params["post_type"] = post_type
    if limit:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/severities",
        params=params,
        maximum_records=limit or DEFAULT_PAGINATION_LIMIT,
    )

    severities = [StatusPageSeverity(**item) for item in response]
    return ListResponseModel[StatusPageSeverity](response=severities)


def list_status_page_impacts(
    status_page_id: str,
    post_type: Literal["incident", "maintenance"] | None = None,
    limit: int | None = DEFAULT_PAGINATION_LIMIT,
) -> ListResponseModel[StatusPageImpact]:
    """List Impacts for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        post_type: Filter by post type: 'incident' or 'maintenance'.
        limit: Maximum number of results to return. Default 20.

    Returns:
        List of StatusPageImpact objects for the given Status Page
    """
    params: dict[str, Any] = {}
    if post_type:
        params["post_type"] = post_type
    if limit:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/impacts",
        params=params,
        maximum_records=limit or DEFAULT_PAGINATION_LIMIT,
    )

    impacts = [StatusPageImpact(**item) for item in response]
    return ListResponseModel[StatusPageImpact](response=impacts)


def list_status_page_statuses(
    status_page_id: str,
    post_type: Literal["incident", "maintenance"] | None = None,
    limit: int | None = DEFAULT_PAGINATION_LIMIT,
) -> ListResponseModel[StatusPageStatus]:
    """List Statuses for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        post_type: Filter by post type: 'incident' or 'maintenance'.
        limit: Maximum number of results to return. Default 20.

    Returns:
        List of StatusPageStatus objects for the given Status Page
    """
    params: dict[str, Any] = {}
    if post_type:
        params["post_type"] = post_type
    if limit:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/statuses",
        params=params,
        maximum_records=limit or DEFAULT_PAGINATION_LIMIT,
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
    response = get_client().rpost(
        f"/status_pages/{status_page_id}/posts", json=create_model.model_dump(mode="json")
    )

    return StatusPagePost.from_api_response(response)


def get_status_page_post(
    status_page_id: str,
    post_id: str,
    include: list[str] | None = None,
) -> StatusPagePost:
    """Get a Post for a Status Page by Status Page ID and Post ID.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        include: Optional list of related resources to include (e.g. 'post_updates').

    Returns:
        StatusPagePost details
    """
    params: dict[str, Any] = {}
    if include:
        params["include[]"] = include
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
    status_page_id: str,
    post_id: str,
    reviewed_status: Literal["approved", "not_reviewed"] | None = None,
    limit: int | None = DEFAULT_PAGINATION_LIMIT,
) -> ListResponseModel[StatusPagePostUpdate]:
    """List Post Updates for a Status Page by Status Page ID and Post ID.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        reviewed_status: Filter by review status: 'approved' or 'not_reviewed'.
        limit: Maximum number of results to return. Default 20.

    Returns:
        List of StatusPagePostUpdate objects for the given Post
    """
    params: dict[str, Any] = {}
    if reviewed_status:
        params["reviewed_status"] = reviewed_status
    if limit:
        params["limit"] = limit

    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/posts/{post_id}/post_updates",
        params=params,
        maximum_records=limit or DEFAULT_PAGINATION_LIMIT,
    )

    post_updates = [StatusPagePostUpdate(**item) for item in response]
    return ListResponseModel[StatusPagePostUpdate](response=post_updates)


def list_status_page_posts(status_page_id: str) -> str:
    """List Posts for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page

    Returns:
        JSON string containing a list of posts for the given Status Page
    """
    response = paginate(
        client=get_client(),
        entity=f"/status_pages/{status_page_id}/posts",
        params={},
        maximum_records=100,
    )
    return json.dumps({"response": response})


