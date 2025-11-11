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

    Examples:
        Basic usage:

        >>> from pagerduty_mcp.models.status_pages import StatusPageQuery
        >>> result = list_status_pages(StatusPageQuery())
        >>> isinstance(result.response, list)
        True

        Filter by type:

        >>> result = list_status_pages(StatusPageQuery(status_page_type="public"))
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

    Examples:
        Basic usage:

        >>> from pagerduty_mcp.models.status_pages import StatusPageSeverityQuery
        >>> result = list_status_page_severities("PT4KHLK", StatusPageSeverityQuery())
        >>> isinstance(result.response, list)
        True

        Filter by post type:

        >>> result = list_status_page_severities("PT4KHLK", StatusPageSeverityQuery(post_type="incident"))
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

    Examples:
        Basic usage:

        >>> from pagerduty_mcp.models.status_pages import StatusPageImpactQuery
        >>> result = list_status_page_impacts("PT4KHLK", StatusPageImpactQuery())
        >>> isinstance(result.response, list)
        True

        Filter by post type:

        >>> result = list_status_page_impacts("PT4KHLK", StatusPageImpactQuery(post_type="maintenance"))
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

    Examples:
        Basic usage:

        >>> from pagerduty_mcp.models.status_pages import StatusPageStatusQuery
        >>> result = list_status_page_statuses("PT4KHLK", StatusPageStatusQuery())
        >>> isinstance(result.response, list)
        True

        Filter by post type:

        >>> result = list_status_page_statuses("PT4KHLK", StatusPageStatusQuery(post_type="incident"))
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


def create_status_page_post(
    status_page_id: str, create_model: StatusPagePostCreateRequestWrapper
) -> StatusPagePost:
    """Create a Post for a Status Page by Status Page ID.

    Args:
        status_page_id: The ID of the Status Page
        create_model: The post creation request

    Returns:
        The created StatusPagePost

    Examples:
        Create a maintenance post:

        >>> from pagerduty_mcp.models.status_pages import (
        ...     StatusPagePostCreateRequestWrapper,
        ...     StatusPagePostCreateRequest,
        ...     StatusPagePostUpdateRequest,
        ...     StatusPageReference,
        ...     StatusPageStatusReference,
        ...     StatusPageSeverityReference,
        ...     StatusPagePostUpdateImpact,
        ...     StatusPageServiceReference,
        ...     StatusPageImpactReference
        ... )
        >>> from datetime import datetime
        >>> update = StatusPagePostUpdateRequest(
        ...     message="<p>Scheduled maintenance</p>",
        ...     status=StatusPageStatusReference(id="P0400H4"),
        ...     severity=StatusPageSeverityReference(id="PY5OM08"),
        ...     impacted_services=[
        ...         StatusPagePostUpdateImpact(
        ...             service=StatusPageServiceReference(id="PYHMEI3"),
        ...             impact=StatusPageImpactReference(id="PY5OM08")
        ...         )
        ...     ],
        ...     notify_subscribers=False,
        ...     update_frequency_ms=None
        ... )
        >>> post_request = StatusPagePostCreateRequest(
        ...     title="Database Upgrade",
        ...     post_type="maintenance",
        ...     starts_at=datetime(2023, 12, 12, 11, 0, 0),
        ...     ends_at=datetime(2023, 12, 12, 12, 0, 0),
        ...     updates=[update],
        ...     status_page=StatusPageReference(id="PR5LMML")
        ... )
        >>> wrapper = StatusPagePostCreateRequestWrapper(post=post_request)
        >>> result = create_status_page_post("PR5LMML", wrapper)
        >>> isinstance(result, StatusPagePost)
        True
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

    Examples:
        Get a specific post:

        >>> from pagerduty_mcp.models.status_pages import StatusPagePostQuery
        >>> result = get_status_page_post("PR5LMML", "PIJ90N7", StatusPagePostQuery())
        >>> isinstance(result, StatusPagePost)
        True

        Include post updates:

        >>> result = get_status_page_post(
        ...     "PR5LMML",
        ...     "PIJ90N7",
        ...     StatusPagePostQuery(include=["status_page_post_update"])
        ... )
    """
    params = query_model.to_params()
    response = get_client().rget(f"/status_pages/{status_page_id}/posts/{post_id}", params=params)

    return StatusPagePost.from_api_response(response)


def create_status_page_post_update(
    status_page_id: str, post_id: str, create_model: StatusPagePostUpdateRequestWrapper
) -> StatusPagePostUpdate:
    """Create a Post Update for a Post by Post ID.

    Args:
        status_page_id: The ID of the Status Page
        post_id: The ID of the Status Page Post
        create_model: The post update creation request

    Returns:
        The created StatusPagePostUpdate

    Examples:
        Create a post update:

        >>> from pagerduty_mcp.models.status_pages import (
        ...     StatusPagePostUpdateRequestWrapper,
        ...     StatusPagePostUpdateRequest,
        ...     StatusPagePostReference,
        ...     StatusPageStatusReference,
        ...     StatusPageSeverityReference,
        ...     StatusPagePostUpdateImpact,
        ...     StatusPageServiceReference,
        ...     StatusPageImpactReference
        ... )
        >>> update_request = StatusPagePostUpdateRequest(
        ...     message="<p>Investigation ongoing</p>",
        ...     status=StatusPageStatusReference(id="P0400H4"),
        ...     severity=StatusPageSeverityReference(id="PY5OM08"),
        ...     impacted_services=[
        ...         StatusPagePostUpdateImpact(
        ...             service=StatusPageServiceReference(id="PYHMEI3"),
        ...             impact=StatusPageImpactReference(id="PY5OM08")
        ...         )
        ...     ],
        ...     notify_subscribers=False,
        ...     update_frequency_ms=300000,
        ...     post=StatusPagePostReference(id="P6F2CJ3")
        ... )
        >>> wrapper = StatusPagePostUpdateRequestWrapper(post_update=update_request)
        >>> result = create_status_page_post_update("PR5LMML", "P6F2CJ3", wrapper)
        >>> isinstance(result, StatusPagePostUpdate)
        True
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

    Examples:
        Basic usage:

        >>> from pagerduty_mcp.models.status_pages import StatusPagePostUpdateQuery
        >>> result = list_status_page_post_updates("PR5LMML", "PIJ90N7", StatusPagePostUpdateQuery())
        >>> isinstance(result.response, list)
        True

        Filter by reviewed status:

        >>> result = list_status_page_post_updates(
        ...     "PR5LMML",
        ...     "PIJ90N7",
        ...     StatusPagePostUpdateQuery(reviewed_status="approved")
        ... )
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
