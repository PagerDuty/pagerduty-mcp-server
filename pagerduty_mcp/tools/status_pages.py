from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    StatusPage,
    StatusPageImpact,
    StatusPageImpactQuery,
    StatusPagePost,
    StatusPagePostCreateRequest,
    StatusPagePostUpdate,
    StatusPagePostUpdateRequestBody,
    StatusPageQuery,
    StatusPageSeverity,
    StatusPageSeverityQuery,
    StatusPageStatus,
    StatusPageStatusQuery,
)
from pagerduty_mcp.utils import paginate


def list_status_pages(query_model: StatusPageQuery) -> ListResponseModel[StatusPage]:
    """List Status Pages.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of StatusPage objects matching the query parameters

    Examples:
        Basic usage:

        >>> from pagerduty_mcp.models import StatusPageQuery
        >>> result = list_status_pages(StatusPageQuery())
        >>> isinstance(result.response, list)
        True

        Filter by type:

        >>> result = list_status_pages(StatusPageQuery(status_page_type="public"))
    """
    params = query_model.to_params()
    response = paginate(client=get_client(), entity="status_pages", params=params)
    status_pages = [StatusPage(**sp) for sp in response]
    return ListResponseModel[StatusPage](response=status_pages)


def list_status_page_severities(
    status_page_id: str, query_model: StatusPageSeverityQuery
) -> ListResponseModel[StatusPageSeverity]:
    """List Severities for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        query_model: Optional filtering parameters

    Returns:
        List of StatusPageSeverity objects

    Examples:
        List all severities:

        >>> from pagerduty_mcp.models import StatusPageSeverityQuery
        >>> result = list_status_page_severities("PT4KHLK", StatusPageSeverityQuery())
        >>> isinstance(result.response, list)
        True

        Filter by post type:

        >>> result = list_status_page_severities("PT4KHLK", StatusPageSeverityQuery(post_type="incident"))
    """
    params = query_model.to_params()
    response = paginate(client=get_client(), entity=f"status_pages/{status_page_id}/severities", params=params)
    severities = [StatusPageSeverity(**severity) for severity in response]
    return ListResponseModel[StatusPageSeverity](response=severities)


def list_status_page_impacts(
    status_page_id: str, query_model: StatusPageImpactQuery
) -> ListResponseModel[StatusPageImpact]:
    """List Impacts for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        query_model: Optional filtering parameters

    Returns:
        List of StatusPageImpact objects

    Examples:
        List all impacts:

        >>> from pagerduty_mcp.models import StatusPageImpactQuery
        >>> result = list_status_page_impacts("PT4KHLK", StatusPageImpactQuery())
        >>> isinstance(result.response, list)
        True

        Filter by post type:

        >>> result = list_status_page_impacts("PT4KHLK", StatusPageImpactQuery(post_type="maintenance"))
    """
    params = query_model.to_params()
    response = paginate(client=get_client(), entity=f"status_pages/{status_page_id}/impacts", params=params)
    impacts = [StatusPageImpact(**impact) for impact in response]
    return ListResponseModel[StatusPageImpact](response=impacts)


def list_status_page_statuses(
    status_page_id: str, query_model: StatusPageStatusQuery
) -> ListResponseModel[StatusPageStatus]:
    """List Statuses for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        query_model: Optional filtering parameters

    Returns:
        List of StatusPageStatus objects

    Examples:
        List all statuses:

        >>> from pagerduty_mcp.models import StatusPageStatusQuery
        >>> result = list_status_page_statuses("PT4KHLK", StatusPageStatusQuery())
        >>> isinstance(result.response, list)
        True

        Filter by post type:

        >>> result = list_status_page_statuses("PT4KHLK", StatusPageStatusQuery(post_type="incident"))
    """
    params = query_model.to_params()
    response = paginate(client=get_client(), entity=f"status_pages/{status_page_id}/statuses", params=params)
    statuses = [StatusPageStatus(**status) for status in response]
    return ListResponseModel[StatusPageStatus](response=statuses)


def create_status_page_post(status_page_id: str, post_data: StatusPagePostCreateRequest) -> StatusPagePost:
    """Create a Post for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        post_data: The post data to create

    Returns:
        The created StatusPagePost

    Examples:
        Create a maintenance post:

        >>> from pagerduty_mcp.models import StatusPagePostCreateRequest, StatusPagePostCreate
        >>> from datetime import datetime
        >>> post = StatusPagePostCreate(
        ...     title="Scheduled Maintenance",
        ...     post_type="maintenance",
        ...     starts_at=datetime(2024, 12, 1, 10, 0, 0),
        ...     ends_at=datetime(2024, 12, 1, 12, 0, 0)
        ... )
        >>> request = StatusPagePostCreateRequest(post=post)
        >>> result = create_status_page_post("PT4KHLK", request)
    """
    response = get_client().rpost(f"/status_pages/{status_page_id}/posts", json=post_data.model_dump(exclude_none=True))
    return StatusPagePost.from_api_response(response)


def get_status_page_post(status_page_id: str, post_id: str) -> StatusPagePost:
    """Get a Post for a Status Page by Status Page ID and Post ID.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Post

    Returns:
        StatusPagePost details

    Examples:
        Get a post:

        >>> result = get_status_page_post("PT4KHLK", "POST123")
        >>> result.id
        'POST123'
    """
    response = get_client().rget(f"/status_pages/{status_page_id}/posts/{post_id}")
    return StatusPagePost.from_api_response(response)


def create_status_page_post_update(
    status_page_id: str, post_id: str, update_data: StatusPagePostUpdateRequestBody
) -> StatusPagePostUpdate:
    """Create a Post Update for a Status Page Post.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Post
        update_data: The post update data

    Returns:
        The created StatusPagePostUpdate

    Examples:
        Create a post update:

        >>> from pagerduty_mcp.models import (
        ...     StatusPagePostUpdateRequestBody,
        ...     StatusPagePostUpdateRequest,
        ...     StatusPageSeverityReference,
        ...     StatusPageStatusReference
        ... )
        >>> update = StatusPagePostUpdateRequest(
        ...     message="Issue has been resolved",
        ...     severity=StatusPageSeverityReference(id="SEV123"),
        ...     status=StatusPageStatusReference(id="STAT123")
        ... )
        >>> request = StatusPagePostUpdateRequestBody(post_update=update)
        >>> result = create_status_page_post_update("PT4KHLK", "POST123", request)
    """
    response = get_client().rpost(
        f"/status_pages/{status_page_id}/posts/{post_id}/post_updates",
        json=update_data.model_dump(exclude_none=True),
    )

    if isinstance(response, dict) and "post_update" in response:
        return StatusPagePostUpdate.model_validate(response["post_update"])

    return StatusPagePostUpdate.model_validate(response)


def list_status_page_post_updates(status_page_id: str, post_id: str) -> ListResponseModel[StatusPagePostUpdate]:
    """List Post Updates for a Status Page Post.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Post

    Returns:
        List of StatusPagePostUpdate objects

    Examples:
        List all post updates:

        >>> result = list_status_page_post_updates("PT4KHLK", "POST123")
        >>> isinstance(result.response, list)
        True
    """
    response = paginate(
        client=get_client(), entity=f"status_pages/{status_page_id}/posts/{post_id}/post_updates", params={}
    )
    updates = [StatusPagePostUpdate(**update) for update in response]
    return ListResponseModel[StatusPagePostUpdate](response=updates)
