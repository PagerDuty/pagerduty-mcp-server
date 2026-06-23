import logging
from typing import Literal

from pagerduty.errors import HttpError

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Schedule,
    ScheduleDetail,
    ScheduleOverrideCreate,
    ScheduleQuery,
    SchedulesListResponse,
    ScheduleSummary,
    ScheduleV3Create,
    ScheduleV3Update,
    SourceStatus,
    User,
)
from pagerduty_mcp.tools.schedules_v3 import (
    _get_v3_schedules_page,
    create_schedule_v3,
    get_schedule_v3,
    update_schedule_v3,
)
from pagerduty_mcp.utils import paginate

logger = logging.getLogger(__name__)

# Shift-based (v3) names are absent from the v3 list endpoint, so we enrich via per-id GETs.
# Bounded to avoid an N+1 blow-up on large accounts; names beyond the cap stay null.
_V3_ENRICH_CAP = 50

# The cross-namespace v2 GET returns a 400 whose message points at the v3 API. Matching the
# specific message (not just the 400 status) means a genuine bad-request is never swallowed.
_V3_REDIRECT_MARKERS = ("shift-based", "v3 schedules api", "/v3/schedules")


def _v2_summary(raw: dict) -> ScheduleSummary:
    return ScheduleSummary(
        id=raw["id"],
        name=raw.get("name"),
        kind="layer_based",
        time_zone=raw.get("time_zone"),
        html_url=raw.get("html_url"),
        summary=raw.get("summary"),
    )


def _list_v3_summaries(query_model: ScheduleQuery, *, enrich: bool) -> tuple[list[ScheduleSummary], bool, int]:
    """Return shift-based (v3) summaries, whether more pages exist, and how many names were left null.

    v3 LIST only supports name `query` and `limit`, so other v2 filters are not forwarded.
    """
    raw_refs, more = _get_v3_schedules_page(query=query_model.query, limit=query_model.limit)

    summaries: list[ScheduleSummary] = []
    unenriched = 0
    enriched = 0
    for ref in raw_refs:
        schedule_id = ref.get("id")
        if not schedule_id:
            continue
        name = ref.get("name")
        time_zone = ref.get("time_zone")
        html_url = ref.get("html_url")

        if name is None:
            if enrich and enriched < _V3_ENRICH_CAP:
                try:
                    full = get_schedule_v3(schedule_id)
                    name = full.name
                    time_zone = time_zone or full.time_zone
                    html_url = html_url or full.html_url
                    enriched += 1
                except Exception as exc:  # noqa: BLE001 - one enrichment miss must not drop the item or fail the list
                    unenriched += 1
                    logger.warning("v3 schedule %s name enrichment failed: %s", schedule_id, exc)
            else:
                unenriched += 1

        summaries.append(
            ScheduleSummary(
                id=schedule_id,
                name=name,
                kind="shift_based",
                time_zone=time_zone,
                html_url=html_url,
                summary=ref.get("summary"),
            )
        )
    return summaries, more, unenriched


def list_schedules(query_model: ScheduleQuery, *, enrich: bool = True) -> SchedulesListResponse:
    """List ALL PagerDuty schedules across BOTH scheduling systems in a single call.

    This returns classic layer-based (v2) schedules AND next-gen shift-based (v3) schedules
    together. It is the complete, authoritative schedule list — there is no other list tool.
    Each item's `kind` field ("layer_based" or "shift_based") says which system it belongs to.
    If either source fails, `response_summary`/`sources` explicitly mark the list INCOMPLETE;
    otherwise treat it as exhaustive. Never tell the user a schedule type is unsupported or missing.

    Args:
        query_model: Filters (name query, team_ids, user_ids, limit). Shift-based (v3) schedules
            are filtered by name `query` and `limit` only.
        enrich: When True (default), fill in names for shift-based (v3) schedules (bounded to the
            returned page, max 50). Set False to skip the extra lookups; v3 names may then be null.

    Returns:
        The merged schedule summaries with per-source status and a `degraded` flag.
    """
    summaries: list[ScheduleSummary] = []
    sources: list[SourceStatus] = []
    degraded = False

    # Each source is retrieved independently: one system failing must never hide the other,
    # and must never be mistaken for "no schedules exist".
    try:
        v2_raw = paginate(client=get_client(), entity="schedules", params=query_model.to_params())
        summaries.extend(_v2_summary(raw) for raw in v2_raw)
        sources.append(SourceStatus(api="v2", status="ok", count=len(v2_raw)))
    except Exception as exc:  # noqa: BLE001 - resilience: report the failure, keep the other source
        degraded = True
        sources.append(SourceStatus(api="v2", status="error", message=str(exc)))
        logger.warning("Listing layer-based (v2) schedules failed: %s", exc)

    try:
        v3_summaries, v3_more, unenriched = _list_v3_summaries(query_model, enrich=enrich)
        summaries.extend(v3_summaries)
        note = f"{unenriched} shift-based name(s) not enriched (cap reached or enrich disabled)" if unenriched else None
        sources.append(SourceStatus(api="v3", status="ok", count=len(v3_summaries), more=v3_more, message=note))
    except Exception as exc:  # noqa: BLE001 - resilience: report the failure, keep the other source
        degraded = True
        sources.append(SourceStatus(api="v3", status="error", message=str(exc)))
        logger.warning("Listing shift-based (v3) schedules failed: %s", exc)

    return SchedulesListResponse(response=summaries, sources=sources, degraded=degraded)


def _get_v2(schedule_id: str) -> Schedule:
    return Schedule.model_validate(get_client().rget(f"/schedules/{schedule_id}"))


def _is_v3_redirect(exc: HttpError) -> bool:
    """True only for the specific 'this is a shift-based schedule, use v3' 400."""
    resp = getattr(exc, "response", None)
    if resp is None or getattr(resp, "status_code", None) != 400:
        return False
    try:
        body = resp.json()
        message = (body.get("error") or {}).get("message", "") if isinstance(body, dict) else ""
    except Exception:  # noqa: BLE001 - fall back to the raw text
        message = getattr(resp, "text", "") or ""
    message = (message or "").lower()
    return any(marker in message for marker in _V3_REDIRECT_MARKERS)


def get_schedule(schedule_id: str, kind: Literal["layer_based", "shift_based"] | None = None) -> ScheduleDetail:
    """Get a single schedule by ID — works for layer-based (v2) and shift-based (v3) schedules alike.

    You normally do not need to know the kind in advance; this resolves it automatically.

    Args:
        schedule_id: The ID of the schedule to retrieve.
        kind: Optional hint ("layer_based" or "shift_based", taken from a prior list result) to
            skip an extra lookup. A wrong or omitted hint still resolves correctly.

    Returns:
        The schedule details (a layer-based Schedule or a shift-based ScheduleV3).
    """
    if kind == "shift_based":
        return get_schedule_v3(schedule_id)
    if kind == "layer_based":
        return _get_v2(schedule_id)

    # No hint: try the layer-based (v2) endpoint, and on its self-describing 400 fall back to v3.
    try:
        return _get_v2(schedule_id)
    except HttpError as exc:
        if _is_v3_redirect(exc):
            return get_schedule_v3(schedule_id)
        raise


def create_schedule(schedule_data: ScheduleV3Create) -> ScheduleDetail:
    """Create a new schedule. All new schedules use PagerDuty's next-gen shift-based (v3) system.

    Args:
        schedule_data: Name, time_zone, and rotations for the new shift-based schedule.

    Returns:
        The created schedule.
    """
    return create_schedule_v3(schedule_data)


def update_schedule(schedule_id: str, schedule_data: ScheduleV3Update) -> ScheduleDetail:
    """Update an existing shift-based (v3) schedule.

    Classic layer-based (v2) schedules cannot be edited through this tool; attempting to update
    one surfaces the PagerDuty API's guidance message rather than failing silently.

    Args:
        schedule_id: The ID of the shift-based (v3) schedule to update.
        schedule_data: Fields to change (only provided fields are updated).

    Returns:
        The updated schedule.
    """
    return update_schedule_v3(schedule_id, schedule_data)


def create_schedule_override(schedule_id: str, override_request: ScheduleOverrideCreate) -> dict | list:
    """Create an override for a schedule.

    Args:
        schedule_id: The ID of the schedule to override
        override_request: Data for the schedule override

    Returns:
        The created schedule override
    """
    for override in override_request.overrides:
        override.start = override.start.isoformat()
        override.end = override.end.isoformat()

    return get_client().rpost(f"/schedules/{schedule_id}/overrides", json=override_request.model_dump())


def list_schedule_users(schedule_id: str) -> ListResponseModel[User]:
    """List users in a schedule.

    Args:
        schedule_id: The ID of the schedule

    Returns:
        List of users in the schedule
    """
    response = get_client().rget(f"/schedules/{schedule_id}/users")
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)
