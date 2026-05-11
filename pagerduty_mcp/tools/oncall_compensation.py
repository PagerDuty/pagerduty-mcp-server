"""
Agentic On-Call Compensation Report tool.

Replicates the full computation pipeline of the UI app server-side so agents
can query, filter, and reason over the results without opening a browser.

Data sources (same as the UI):
  - /analytics/metrics/responders/teams  — oncall hours + interruption breakdown
  - list_oncalls                          — raw shift windows for outside-hours math
  - list_incidents                        — per-user urgency counts
  - list_teams / list_users              — name resolution + timezone
  - list_escalation_policies             — EP filter support
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pagerduty_mcp.client import get_client
from pagerduty_mcp.utils import paginate


# ── Compliance templates ──────────────────────────────────────────────────────

COMPLIANCE_TEMPLATES: dict[str, dict] = {
    # EU Working Time Directive: 48h/week avg over 4 weeks, 11h daily rest, max 6 consecutive days
    "emea": dict(hours_cap=192, outside_hours_cap=80, max_consecutive_days=6,
                 max_consecutive_hours=48, min_rest_hours=11),
    # US: 40h/week × 4 weeks, 8h rest, max 7 consecutive days
    "us": dict(hours_cap=160, outside_hours_cap=60, max_consecutive_days=7,
               max_consecutive_hours=72, min_rest_hours=8),
    # No compliance limits (default) — use for pay/burden reporting
    "none": dict(hours_cap=0, outside_hours_cap=0, max_consecutive_days=0,
                 max_consecutive_hours=0, min_rest_hours=0),
}


# ── Request model ────────────────────────────────────────────────────────────

class OncallCompensationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    since: str = Field(
        description="Start of reporting period in ISO 8601 format (e.g. '2026-01-01T00:00:00Z'). "
                    "Inclusive. Maximum recommended range: 90 days."
    )
    until: str = Field(
        description="End of reporting period in ISO 8601 format (e.g. '2026-01-31T23:59:59Z'). "
                    "Exclusive."
    )
    team_ids: list[str] | None = Field(
        default=None,
        description="Restrict report to specific team IDs. Leave null for all teams."
    )
    escalation_policy_id: str | None = Field(
        default=None,
        description="Restrict report to users in a specific escalation policy."
    )
    # Compliance / limits template
    compliance_template: str = Field(
        default="none",
        description=(
            "Pre-built compliance rule set. Determines the thresholds used in "
            "compliance_flags on each user. Options:\n"
            "  'emea'  — EU Working Time Directive: 192h/period cap, 11h rest, max 6 consecutive days\n"
            "  'us'    — US defaults: 160h/period cap, 8h rest, max 7 consecutive days\n"
            "  'none'  — No compliance checks (default). Use when you only need burden/pay data.\n"
            "Custom overrides: set hours_cap, outside_hours_cap, max_consecutive_days, "
            "max_consecutive_hours, or min_rest_hours to non-zero values alongside any template."
        )
    )
    # Custom compliance overrides (0 = inherit from template or disabled)
    hours_cap: float = Field(
        default=0.0, ge=0,
        description="Override: max scheduled hours allowed per period. 0 = use template value."
    )
    outside_hours_cap: float = Field(
        default=0.0, ge=0,
        description="Override: max outside-business-hours allowed per period. 0 = use template value."
    )
    max_consecutive_days: int = Field(
        default=0, ge=0,
        description="Override: max consecutive calendar days on-call. 0 = use template value."
    )
    max_consecutive_hours: float = Field(
        default=0.0, ge=0,
        description="Override: max single unbroken on-call shift in hours. 0 = use template value."
    )
    min_rest_hours: float = Field(
        default=0.0, ge=0,
        description="Override: minimum hours of rest required between consecutive shifts. 0 = use template value."
    )
    # Business hours config
    biz_start_hour: int = Field(
        default=9, ge=0, le=23,
        description="Local hour when business hours begin (inclusive). Default 9 = 09:00."
    )
    biz_end_hour: int = Field(
        default=18, ge=1, le=24,
        description="Local hour when business hours end (exclusive). Default 18 = 18:00."
    )
    timezone: str = Field(
        default="UTC",
        description="IANA timezone for business-hours and weekend classification "
                    "(e.g. 'America/New_York', 'Europe/London'). Default UTC."
    )
    work_days: list[int] = Field(
        default=[1, 2, 3, 4, 5],
        description="ISO weekday numbers that are business days. 1=Monday … 7=Sunday. "
                    "Default Mon–Fri."
    )
    holidays: list[str] = Field(
        default=[],
        description="List of holiday dates as 'YYYY-MM-DD' strings in the configured timezone. "
                    "Shifts on these dates count as holiday hours."
    )
    # Pay config
    l1_rate_per_hour: float = Field(
        default=0.0, ge=0,
        description="Hourly pay rate for L1 on-call during business hours. "
                    "Set to 0 to skip pay estimation."
    )
    l2_plus_rate_per_hour: float = Field(
        default=0.0, ge=0,
        description="Hourly pay rate for L2+ on-call shifts. Set to 0 to skip."
    )
    off_hours_multiplier: float = Field(
        default=1.5, ge=1,
        description="Multiplier applied to l1_rate_per_hour for weekday off-hours shifts."
    )
    weekend_multiplier: float = Field(
        default=2.0, ge=1,
        description="Multiplier applied to l1_rate_per_hour for weekend shifts."
    )
    holiday_multiplier: float = Field(
        default=2.5, ge=1,
        description="Multiplier applied to l1_rate_per_hour for holiday shifts."
    )
    # Output control
    include_incidents: bool = Field(
        default=False,
        description="Include per-user incident list in the response. "
                    "Adds detail but increases response size significantly."
    )
    include_directly_added: bool = Field(
        default=False,
        description="Include on-call entries that were added directly to an escalation policy "
                    "layer (not backed by a schedule). Default False."
    )
    min_scheduled_hours: float = Field(
        default=0.0,
        ge=0,
        description="Exclude users with fewer scheduled hours than this threshold. "
                    "Useful to filter out noise from users briefly added to policies."
    )


# ── Output models ─────────────────────────────────────────────────────────────

class UserCompensationSummary(BaseModel):
    user_id: str
    user_name: str
    user_timezone: str | None = None
    team_names: list[str]

    # On-call hours (from Analytics — authoritative, deduped)
    scheduled_hours: float
    scheduled_hours_l1: float
    scheduled_hours_l2_plus: float

    # Interruption breakdown (PagerDuty native categories, from Analytics)
    total_interruptions: int
    business_hour_interruptions: int
    off_hour_interruptions: int
    sleep_hour_interruptions: int
    interruption_rate: float  # interruptions per scheduled hour
    mean_time_to_ack_seconds: float

    # Incident counts
    incident_count: int
    incident_hours: float
    high_urgency_incidents: int
    low_urgency_incidents: int

    # Outside-hours breakdown (computed from raw shifts + biz-hours config)
    outside_hours: float       # total off-hours: weekday OOH + weekends + holidays
    weekend_hours: float
    holiday_hours: float
    weeknight_hours: float     # weekday outside-hours only
    weekend_period_count: int  # distinct weekends touched
    holiday_count: int         # distinct holidays touched
    unique_ooh_periods: int    # total distinct outside-hours segments

    # Fatigue / compliance signals
    max_consecutive_on_call_hours: float
    max_consecutive_on_call_days: int
    min_rest_hours: float      # shortest gap between consecutive shifts; 999 = no gap

    # Estimated pay (0 if l1_rate_per_hour=0)
    estimated_pay: float

    # Compliance flags (populated when compliance_template != 'none' or custom limits set)
    compliance_status: str = "ok"         # "ok" | "near" | "over"
    compliance_flags: list[str] = Field(  # human-readable list of triggered limits
        default_factory=list,
        description="List of triggered compliance rules, e.g. 'hours_cap exceeded (192h limit)'."
    )


class OncallCompensationReport(BaseModel):
    since: str
    until: str
    timezone: str
    compliance_template: str
    generated_at: str
    total_users: int
    total_scheduled_hours: float
    total_outside_hours: float
    total_estimated_pay: float
    compliance_violations: int  # users with status "over"
    compliance_near_limit: int  # users with status "near"
    users: list[UserCompensationSummary]
    # Summary by team
    team_summary: list[dict[str, Any]]


# ── Business-hours computation (pure Python port of businessHours.ts) ─────────

def _get_tz_parts(ts_ms: float, tz: str) -> dict[str, Any]:
    """Return year/month/day/hour/weekday for a UTC timestamp in given IANA tz."""
    from zoneinfo import ZoneInfo
    dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=ZoneInfo(tz))
    return {
        "year": dt.year, "month": dt.month, "day": dt.day,
        "hour": dt.hour, "minute": dt.minute,
        "weekday": dt.isoweekday(),  # 1=Mon … 7=Sun
        "date_str": dt.strftime("%Y-%m-%d"),
    }


def _midnight_ms(date_str: str, tz: str) -> float:
    """UTC milliseconds for local midnight on date_str in tz."""
    from zoneinfo import ZoneInfo
    y, m, d = (int(x) for x in date_str.split("-"))
    dt = datetime(y, m, d, 0, 0, tzinfo=ZoneInfo(tz))
    return dt.timestamp() * 1000.0


def _days_in_range(start_ms: float, end_ms: float, tz: str) -> list[str]:
    """All local date strings 'YYYY-MM-DD' overlapping [start_ms, end_ms)."""
    seen: set[str] = set()
    result: list[str] = []
    t = start_ms
    step = 6 * 3_600_000  # 6 hours
    while t < end_ms:
        ds = _get_tz_parts(t, tz)["date_str"]
        if ds not in seen:
            seen.add(ds)
            result.append(ds)
        t += step
    last = _get_tz_parts(end_ms - 1, tz)["date_str"]
    if last not in seen:
        result.append(last)
    return result


def _compute_outside_hours(
    shifts: list[dict],
    biz_start: int,
    biz_end: int,
    work_days_iso: set[int],
    holidays: set[str],
    tz: str,
) -> dict[str, float | int]:
    """
    Given merged shift windows, compute outside-hours breakdown.
    shifts: list of {"start": ms, "end": ms}
    Returns dict matching UserCompensationSummary outside-hours fields.
    """
    if not shifts:
        return dict(
            outside_hours=0.0, weekend_hours=0.0, holiday_hours=0.0, weeknight_hours=0.0,
            weekend_period_count=0, holiday_count=0, unique_ooh_periods=0,
            max_consecutive_on_call_hours=0.0, max_consecutive_on_call_days=0, min_rest_hours=999.0,
        )

    # Sort and merge shifts to avoid double-counting
    sorted_shifts = sorted(shifts, key=lambda s: s["start"])
    merged: list[dict] = [dict(sorted_shifts[0])]
    for s in sorted_shifts[1:]:
        if s["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], s["end"])
        else:
            merged.append(dict(s))

    outside_segs: list[dict] = []  # {"start", "end", "category"}
    covered_dates: set[str] = set()
    weekend_iso_weeks: set[str] = set()
    holiday_dates: set[str] = set()

    for shift in merged:
        s_start, s_end = shift["start"], shift["end"]
        for date_str in _days_in_range(s_start, s_end, tz):
            covered_dates.add(date_str)
            parts = _get_tz_parts(_midnight_ms(date_str, tz) + 12 * 3_600_000, tz)  # noon
            iso_wd = parts["weekday"]  # 1=Mon…7=Sun

            # Weekend period tracking (distinct weeks with Sat/Sun coverage)
            if iso_wd in (6, 7):  # Sat=6, Sun=7
                from zoneinfo import ZoneInfo as _ZI
                noon_ms = _midnight_ms(date_str, tz) + 12 * 3_600_000
                noon_dt = datetime.fromtimestamp(noon_ms / 1000.0, tz=_ZI(tz))
                # Use ISO week Monday as week key
                week_start = noon_dt - __import__("datetime").timedelta(days=noon_dt.weekday())
                weekend_iso_weeks.add(week_start.strftime("%Y-%m-%d"))

            if date_str in holidays:
                holiday_dates.add(date_str)

            # Compute outside segments for this day
            y, m, d = (int(x) for x in date_str.split("-"))
            day_start_ms = _midnight_ms(date_str, tz)
            next_date = (datetime(y, m, d, tzinfo=__import__("zoneinfo").ZoneInfo(tz))
                         + __import__("datetime").timedelta(days=1))
            day_end_ms = next_date.timestamp() * 1000.0

            seg_start = max(day_start_ms, s_start)
            seg_end = min(day_end_ms, s_end)
            if seg_start >= seg_end:
                continue

            if date_str in holidays:
                outside_segs.append({"start": seg_start, "end": seg_end, "cat": "holiday"})
            elif iso_wd not in work_days_iso:
                outside_segs.append({"start": seg_start, "end": seg_end, "cat": "weekend"})
            else:
                from zoneinfo import ZoneInfo as _ZI2
                biz_s = datetime(y, m, d, biz_start, 0, tzinfo=_ZI2(tz)).timestamp() * 1000.0
                biz_e = datetime(y, m, d, biz_end, 0, tzinfo=_ZI2(tz)).timestamp() * 1000.0
                if seg_start < biz_s:
                    outside_segs.append({"start": seg_start, "end": min(seg_end, biz_s), "cat": "weeknight"})
                if seg_end > biz_e:
                    outside_segs.append({"start": max(seg_start, biz_e), "end": seg_end, "cat": "weeknight"})

    # Merge outside segments
    def _merge_segs(segs: list[dict]) -> list[dict]:
        if not segs:
            return []
        ss = sorted(segs, key=lambda x: x["start"])
        out = [dict(ss[0])]
        for seg in ss[1:]:
            if seg["start"] <= out[-1]["end"]:
                out[-1]["end"] = max(out[-1]["end"], seg["end"])
            else:
                out.append(dict(seg))
        return out

    merged_segs = _merge_segs(outside_segs)

    h = lambda ms: round(ms / 3_600_000 * 100) / 100

    weekend_ms = sum((s["end"] - s["start"]) for s in outside_segs if s["cat"] == "weekend")
    holiday_ms = sum((s["end"] - s["start"]) for s in outside_segs if s["cat"] == "holiday")
    weeknight_ms = sum((s["end"] - s["start"]) for s in outside_segs if s["cat"] == "weeknight")
    total_outside_ms = sum((s["end"] - s["start"]) for s in merged_segs)

    # Max consecutive on-call days
    sorted_dates = sorted(covered_dates)
    max_consec_days = len(sorted_dates) > 0
    consec = 1
    for i in range(1, len(sorted_dates)):
        prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
        curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        if (curr - prev).days == 1:
            consec += 1
            max_consec_days = max(max_consec_days, consec)
        else:
            consec = 1

    max_shift_ms = max((s["end"] - s["start"]) for s in merged) if merged else 0

    min_rest = 999.0
    for i in range(1, len(merged)):
        gap = (merged[i]["start"] - merged[i - 1]["end"]) / 3_600_000
        min_rest = min(min_rest, gap)

    return dict(
        outside_hours=h(total_outside_ms),
        weekend_hours=h(weekend_ms),
        holiday_hours=h(holiday_ms),
        weeknight_hours=h(weeknight_ms),
        weekend_period_count=len(weekend_iso_weeks),
        holiday_count=len(holiday_dates),
        unique_ooh_periods=len(merged_segs),
        max_consecutive_on_call_hours=h(max_shift_ms),
        max_consecutive_on_call_days=max_consec_days if isinstance(max_consec_days, int) else int(bool(sorted_dates)),
        min_rest_hours=round(min_rest * 100) / 100,
    )


# ── Main tool ─────────────────────────────────────────────────────────────────

def get_oncall_compensation_report(request: OncallCompensationRequest) -> str:
    """Generate an on-call compensation and fairness report for a date range.

    Computes per-user oncall hours, outside-business-hours breakdown (weekends,
    holidays, weeknight off-hours), interruption metrics, and optional pay
    estimates. All computation is done server-side — no UI required.

    Use this tool to:
    - Answer "who was on call the most last month?"
    - Estimate compensation costs for a team or escalation policy
    - Identify responders approaching compliance limits (consecutive days,
      insufficient rest, excessive outside-hours)
    - Compare on-call burden distribution across team members
    - Generate data for payroll exports or HR reporting

    Args:
        request: Date range, optional filters (team/EP), business-hours config,
                 pay rates, and output options.

    Returns:
        JSON string containing OncallCompensationReport with per-user summaries,
        team rollups, and aggregate totals.
    """
    client = get_client()
    since = request.since
    until = request.until
    work_days_iso = set(request.work_days)
    holidays_set = set(request.holidays)
    tz = request.timezone

    # ── Fetch raw data in parallel via the PD REST API ────────────────────────
    # 1. Analytics responder metrics
    analytics_body: dict[str, Any] = {
        "filters": {"date_range_start": since, "date_range_end": until}
    }
    if request.team_ids:
        analytics_body["filters"]["team_ids"] = request.team_ids

    analytics_raw = client.rpost("/analytics/metrics/responders/teams", json=analytics_body)
    if isinstance(analytics_raw, dict):
        analytics_rows = analytics_raw.get("data", [])
    elif isinstance(analytics_raw, list):
        analytics_rows = analytics_raw
    else:
        analytics_rows = []

    # 2. Raw on-call shifts
    oncalls_params: dict[str, Any] = {"since": since, "until": until, "earliest": "false", "limit": 100}
    if request.escalation_policy_id:
        oncalls_params["escalation_policy_ids[]"] = [request.escalation_policy_id]
    oncalls_rows = paginate(client=client, entity="oncalls", params=oncalls_params)

    # 3. Incidents (for urgency breakdown)
    incident_params: dict[str, Any] = {"since": since, "until": until, "limit": 100}
    incident_rows = paginate(client=client, entity="incidents", params=incident_params)

    # 4. Teams + users for name resolution
    teams_rows = paginate(client=client, entity="teams", params={"limit": 100})
    users_rows = paginate(client=client, entity="users", params={"limit": 100})

    # ── Build lookup tables ───────────────────────────────────────────────────
    teams_map: dict[str, str] = {t["id"]: (t.get("name") or t.get("summary") or "Unknown") for t in teams_rows}
    user_tz_map: dict[str, str] = {u["id"]: u["time_zone"] for u in users_rows if u.get("time_zone")}

    # ── Build per-user shifts from list_oncalls ───────────────────────────────
    since_ms = datetime.fromisoformat(since.replace("Z", "+00:00")).timestamp() * 1000.0
    until_ms = datetime.fromisoformat(until.replace("Z", "+00:00")).timestamp() * 1000.0

    user_shifts: dict[str, list[dict]] = {}
    ep_user_ids: set[str] = set()

    for entry in oncalls_rows:
        uid: str | None = (entry.get("user") or {}).get("id")
        if not uid:
            continue
        has_schedule = bool((entry.get("schedule") or {}).get("id"))
        if not request.include_directly_added and not has_schedule:
            continue

        raw_start = entry.get("start")
        raw_end = entry.get("end")
        start_ms = (datetime.fromisoformat(raw_start.replace("Z", "+00:00")).timestamp() * 1000.0
                    if raw_start else since_ms)
        end_ms = (datetime.fromisoformat(raw_end.replace("Z", "+00:00")).timestamp() * 1000.0
                  if raw_end else until_ms)

        start_ms = max(start_ms, since_ms)
        end_ms = min(end_ms, until_ms)
        if start_ms >= end_ms:
            continue

        ep_user_ids.add(uid)
        user_shifts.setdefault(uid, []).append({"start": start_ms, "end": end_ms})

    # ── Build per-user incident records ───────────────────────────────────────
    user_high_urgency: dict[str, int] = {}
    user_low_urgency: dict[str, int] = {}
    user_incidents: dict[str, list[dict]] = {}

    for inc in incident_rows:
        urgency = inc.get("urgency", "low")
        for assignment in inc.get("assignments", []):
            uid = assignment.get("assignee", {}).get("id")
            if not uid:
                continue
            if urgency == "high":
                user_high_urgency[uid] = user_high_urgency.get(uid, 0) + 1
            else:
                user_low_urgency[uid] = user_low_urgency.get(uid, 0) + 1
            if request.include_incidents:
                user_incidents.setdefault(uid, []).append({
                    "id": inc.get("id"),
                    "incident_number": inc.get("incident_number"),
                    "title": inc.get("title", "Untitled"),
                    "urgency": urgency,
                    "created_at": inc.get("created_at"),
                    "resolved_at": inc.get("resolved_at"),
                    "service_name": inc.get("service", {}).get("summary"),
                })

    # ── Merge analytics rows per user ─────────────────────────────────────────
    merged_map: dict[str, dict] = {}

    for row in analytics_rows:
        uid = str(row.get("responder_id") or "")
        if not uid:
            continue

        sched_h = round((row.get("total_seconds_on_call") or 0) / 3600, 2)
        sched_h_l1 = round((row.get("total_seconds_on_call_level_1") or 0) / 3600, 2)
        sched_h_l2 = round((row.get("total_seconds_on_call_level_2_plus") or 0) / 3600, 2)
        total_int = row.get("total_interruptions") or 0
        biz_int = row.get("total_business_hour_interruptions") or 0
        off_int = row.get("total_off_hour_interruptions") or 0
        sleep_int = row.get("total_sleep_hour_interruptions") or 0
        inc_h = round((row.get("total_engaged_seconds") or 0) / 3600, 2)
        inc_count = row.get("total_incident_count") or 0
        mtta = row.get("mean_time_to_acknowledge_seconds") or 0
        team_id = row.get("team_id")
        team_name = (teams_map.get(team_id) if team_id else None) or row.get("team_name")

        if uid in merged_map:
            e = merged_map[uid]
            e["scheduled_hours"] = max(e["scheduled_hours"], sched_h)
            e["scheduled_hours_l1"] = max(e["scheduled_hours_l1"], sched_h_l1)
            e["scheduled_hours_l2_plus"] = max(e["scheduled_hours_l2_plus"], sched_h_l2)
            e["total_interruptions"] += total_int
            e["business_hour_interruptions"] += biz_int
            e["off_hour_interruptions"] += off_int
            e["sleep_hour_interruptions"] += sleep_int
            e["incident_count"] += inc_count
            e["incident_hours"] = round(e["incident_hours"] + inc_h, 2)
            if mtta > 0 and e["mean_time_to_ack_seconds"] == 0:
                e["mean_time_to_ack_seconds"] = mtta
            if team_name and team_name not in e["team_names"]:
                e["team_names"].append(team_name)
        else:
            merged_map[uid] = {
                "user_id": uid,
                "user_name": row.get("responder_name") or "Unknown",
                "user_timezone": user_tz_map.get(uid),
                "team_names": [team_name] if team_name else [],
                "scheduled_hours": sched_h,
                "scheduled_hours_l1": sched_h_l1,
                "scheduled_hours_l2_plus": sched_h_l2,
                "total_interruptions": total_int,
                "business_hour_interruptions": biz_int,
                "off_hour_interruptions": off_int,
                "sleep_hour_interruptions": sleep_int,
                "incident_count": inc_count,
                "incident_hours": inc_h,
                "mean_time_to_ack_seconds": float(mtta),
            }

    # ── Filter by EP if requested ─────────────────────────────────────────────
    if request.escalation_policy_id:
        merged_map = {uid: v for uid, v in merged_map.items() if uid in ep_user_ids}

    # ── Resolve compliance config (template + overrides) ──────────────────────
    tmpl = COMPLIANCE_TEMPLATES.get(request.compliance_template, COMPLIANCE_TEMPLATES["none"])
    eff_hours_cap = request.hours_cap if request.hours_cap > 0 else tmpl["hours_cap"]
    eff_outside_cap = request.outside_hours_cap if request.outside_hours_cap > 0 else tmpl["outside_hours_cap"]
    eff_max_consec_days = request.max_consecutive_days if request.max_consecutive_days > 0 else tmpl["max_consecutive_days"]
    eff_max_consec_hours = request.max_consecutive_hours if request.max_consecutive_hours > 0 else tmpl["max_consecutive_hours"]
    eff_min_rest = request.min_rest_hours if request.min_rest_hours > 0 else tmpl["min_rest_hours"]
    near_threshold = 0.9  # flag at 90% of any limit

    # ── Compute outside-hours + pay per user ──────────────────────────────────
    user_summaries: list[UserCompensationSummary] = []

    for uid, data in merged_map.items():
        sched_h = data["scheduled_hours"]
        if sched_h < request.min_scheduled_hours:
            continue

        shifts = user_shifts.get(uid, [])
        ooh = _compute_outside_hours(shifts, request.biz_start_hour, request.biz_end_hour,
                                     work_days_iso, holidays_set, tz)

        total_int = data["total_interruptions"]
        interruption_rate = round(total_int / sched_h, 3) if sched_h > 0 else 0.0

        # Pay estimation
        estimated_pay = 0.0
        if request.l1_rate_per_hour > 0:
            outside_h = ooh["outside_hours"]
            weekend_h = ooh["weekend_hours"]
            holiday_h = ooh["holiday_hours"]
            weeknight_h = ooh["weeknight_hours"]
            inside_h = max(0.0, sched_h - outside_h)
            estimated_pay = round(
                inside_h * request.l1_rate_per_hour
                + weeknight_h * request.l1_rate_per_hour * request.off_hours_multiplier
                + weekend_h * request.l1_rate_per_hour * request.weekend_multiplier
                + holiday_h * request.l1_rate_per_hour * request.holiday_multiplier
                + data["scheduled_hours_l2_plus"] * request.l2_plus_rate_per_hour,
                2,
            )

        # Compliance evaluation
        flags: list[str] = []
        status = "ok"
        def _check(value: float, cap: float, label: str) -> str | None:
            if cap <= 0:
                return None
            pct = value / cap
            if pct > 1:
                return f"over:{label} ({value:.1f} / {cap:.0f} limit)"
            if pct >= near_threshold:
                return f"near:{label} ({value:.1f} / {cap:.0f} limit, {pct*100:.0f}%)"
            return None

        for flag in [
            _check(sched_h, eff_hours_cap, "hours_cap"),
            _check(ooh["outside_hours"], eff_outside_cap, "outside_hours_cap"),
            _check(ooh["max_consecutive_on_call_days"], eff_max_consec_days, "max_consecutive_days"),
            _check(ooh["max_consecutive_on_call_hours"], eff_max_consec_hours, "max_consecutive_hours"),
        ]:
            if flag:
                flags.append(flag)
                if flag.startswith("over:") and status != "over":
                    status = "over"
                elif flag.startswith("near:") and status == "ok":
                    status = "near"

        if eff_min_rest > 0 and 0 < ooh["min_rest_hours"] < eff_min_rest:
            flags.append(f"over:min_rest_hours ({ooh['min_rest_hours']:.1f}h < {eff_min_rest:.0f}h required)")
            status = "over"

        user_summaries.append(UserCompensationSummary(
            user_id=uid,
            user_name=data["user_name"],
            user_timezone=data.get("user_timezone"),
            team_names=data["team_names"],
            scheduled_hours=sched_h,
            scheduled_hours_l1=data["scheduled_hours_l1"],
            scheduled_hours_l2_plus=data["scheduled_hours_l2_plus"],
            total_interruptions=total_int,
            business_hour_interruptions=data["business_hour_interruptions"],
            off_hour_interruptions=data["off_hour_interruptions"],
            sleep_hour_interruptions=data["sleep_hour_interruptions"],
            interruption_rate=interruption_rate,
            mean_time_to_ack_seconds=data["mean_time_to_ack_seconds"],
            incident_count=data["incident_count"],
            incident_hours=data["incident_hours"],
            high_urgency_incidents=user_high_urgency.get(uid, 0),
            low_urgency_incidents=user_low_urgency.get(uid, 0),
            outside_hours=ooh["outside_hours"],
            weekend_hours=ooh["weekend_hours"],
            holiday_hours=ooh["holiday_hours"],
            weeknight_hours=ooh["weeknight_hours"],
            weekend_period_count=int(ooh["weekend_period_count"]),
            holiday_count=int(ooh["holiday_count"]),
            unique_ooh_periods=int(ooh["unique_ooh_periods"]),
            max_consecutive_on_call_hours=ooh["max_consecutive_on_call_hours"],
            max_consecutive_on_call_days=int(ooh["max_consecutive_on_call_days"]),
            min_rest_hours=ooh["min_rest_hours"],
            estimated_pay=estimated_pay,
            compliance_status=status,
            compliance_flags=flags,
        ))

    user_summaries.sort(key=lambda u: u.scheduled_hours, reverse=True)

    # ── Team rollup ───────────────────────────────────────────────────────────
    team_agg: dict[str, dict] = {}
    for u in user_summaries:
        for tname in (u.team_names or ["(no team)"]):
            t = team_agg.setdefault(tname, dict(
                team_name=tname, user_count=0,
                total_scheduled_hours=0.0, total_outside_hours=0.0,
                total_interruptions=0, total_sleep_interruptions=0,
                total_estimated_pay=0.0,
            ))
            t["user_count"] += 1
            t["total_scheduled_hours"] += u.scheduled_hours
            t["total_outside_hours"] += u.outside_hours
            t["total_interruptions"] += u.total_interruptions
            t["total_sleep_interruptions"] += u.sleep_hour_interruptions
            t["total_estimated_pay"] += u.estimated_pay

    team_summary = sorted(team_agg.values(), key=lambda t: t["total_scheduled_hours"], reverse=True)

    report = OncallCompensationReport(
        since=since,
        until=until,
        timezone=tz,
        compliance_template=request.compliance_template,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_users=len(user_summaries),
        total_scheduled_hours=round(sum(u.scheduled_hours for u in user_summaries), 2),
        total_outside_hours=round(sum(u.outside_hours for u in user_summaries), 2),
        total_estimated_pay=round(sum(u.estimated_pay for u in user_summaries), 2),
        compliance_violations=sum(1 for u in user_summaries if u.compliance_status == "over"),
        compliance_near_limit=sum(1 for u in user_summaries if u.compliance_status == "near"),
        users=user_summaries,
        team_summary=team_summary,
    )

    return report.model_dump_json()
