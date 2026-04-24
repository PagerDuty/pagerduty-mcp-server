/**
 * Operations Intelligence v2 - API layer
 *
 * Fetches pre-aggregated metrics from PagerDuty Analytics API tools.
 * No raw incident list — all metrics are server-side aggregated.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Team {
  id: string;
  name: string;
}

export interface ServiceMetric {
  id: string;
  name: string;
  teamName: string | null;
  totalIncidents: number;
  mttaMinutes: number | null;       // mean_seconds_to_first_ack / 60
  mttrMinutes: number | null;       // mean_seconds_to_resolve / 60
  escalationCount: number;
  uptimePct: number | null;
}

export interface TeamMetric {
  id: string;
  name: string;
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  escalationCount: number;
  totalInterruptions: number;
  uptimePct: number | null;
  // New fatigue fields
  businessHourInterruptions: number;
  offHourInterruptions: number;
  sleepHourInterruptions: number;
  meanEngagedMinutes: number | null;
}

export interface OncallShift {
  userId: string;
  start: number; // UTC ms
  end: number;   // UTC ms
}

export interface ResponderMetric {
  id: string;
  name: string;
  teamName: string | null;
  teamIds: string[];
  onCallHours: number;              // total_seconds_on_call / 3600
  onCallHoursL1: number;            // total_seconds_on_call_level_1 / 3600
  onCallHoursL2Plus: number;        // total_seconds_on_call_level_2_plus / 3600
  totalIncidents: number;
  totalAcks: number;
  sleepInterruptions: number;
  engagedMinutes: number | null;    // total_engaged_seconds / 60
  totalInterruptions: number;
  businessHourInterruptions: number;
  offHourInterruptions: number;
  meanEngagedMinutes: number | null; // mean_engaged_seconds / 60
  riskLevel: "high" | "medium" | "low";
  oncallShifts: OncallShift[];      // raw shift windows for outside-hours computation
}

export interface AggregatedMetrics {
  p50AckSeconds: number | null;
  p75AckSeconds: number | null;
  p90AckSeconds: number | null;
  p95AckSeconds: number | null;
  p50ResolveSeconds: number | null;
  p75ResolveSeconds: number | null;
  p90ResolveSeconds: number | null;
  p95ResolveSeconds: number | null;
}

export interface TrendPoint {
  weekStart: string;       // range_start from API, e.g. "2026-03-17"
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  totalInterruptions: number;
}

export interface TrendsData {
  points: TrendPoint[];    // one entry per week, sorted ascending
}

export interface OpsData {
  teams: Team[];
  selectedTeam: string | null;
  since: string;
  until: string;
  // KPI summary — derived from team aggregate
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  escalationRate: number | null;    // pct: total_escalated / total_incidents * 100
  uptimePct: number | null;
  aggregated: AggregatedMetrics | null;
  trendsData: TrendsData | null;
  // Section data
  serviceMetrics: ServiceMetric[];
  teamMetrics: TeamMetric[];
  responderMetrics: ResponderMetric[];
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function secToMin(seconds: number | null | undefined): number | null {
  if (seconds == null) return null;
  return Math.round(seconds / 60);
}

function secToHours(seconds: number | null | undefined): number {
  if (seconds == null) return 0;
  return Math.round((seconds / 3600) * 10) / 10;
}

const FATIGUE_SLEEP_HIGH = 5;
const FATIGUE_SLEEP_MED = 2;
const FATIGUE_ENGAGED_HIGH_MIN = 480;
const FATIGUE_ENGAGED_MED_MIN = 240;

function computeRisk(sleepInt: number, engagedMin: number | null): "high" | "medium" | "low" {
  if (sleepInt >= FATIGUE_SLEEP_HIGH || (engagedMin !== null && engagedMin >= FATIGUE_ENGAGED_HIGH_MIN)) {
    return "high";
  }
  if (sleepInt >= FATIGUE_SLEEP_MED || (engagedMin !== null && engagedMin >= FATIGUE_ENGAGED_MED_MIN)) {
    return "medium";
  }
  return "low";
}

function buildIncidentFilters(since: string, until: string, teamId: string | null) {
  const filters: Record<string, unknown> = {
    created_at_start: since,
    created_at_end: until,
  };
  if (teamId) filters["team_ids"] = [teamId];
  return filters;
}

// ─── Operational data fetch ───────────────────────────────────────────────────

export async function fetchOpsData(
  app: App,
  since: string,
  until: string,
  teamId: string | null
): Promise<OpsData> {
  if (MOCK_MODE) {
    const { MOCK_OPS_DATA } = await import("./mock");
    return { ...MOCK_OPS_DATA, since, until, selectedTeam: teamId };
  }
  const incidentFilters = buildIncidentFilters(since, until, teamId);
  // Responder endpoint uses date_range_start/end (different field names)
  const responderFilters: Record<string, unknown> = {
    date_range_start: since,
    date_range_end: until,
  };
  if (teamId) responderFilters["team_ids"] = [teamId];

  const [teamsResult, serviceResult, teamResult, responderResult, aggregatedResult, trendsResult, oncallsResult] = await Promise.allSettled([
    app.callServerTool({ name: "list_teams", arguments: { query_model: { limit: 100 } } }),
    app.callServerTool({
      name: "get_incident_metrics_by_service",
      arguments: { request: { filters: incidentFilters } },
    }),
    app.callServerTool({
      name: "get_incident_metrics_by_team",
      arguments: { request: { filters: incidentFilters } },
    }),
    app.callServerTool({
      name: "get_responder_metrics",
      arguments: { request: { filters: responderFilters } },
    }),
    app.callServerTool({
      name: "get_incident_metrics_all",
      arguments: { request: { filters: incidentFilters } },
    }),
    app.callServerTool({
      name: "get_incident_metrics_by_team",
      arguments: { request: { filters: incidentFilters, aggregate_unit: "week" } },
    }),
    app.callServerTool({
      name: "list_oncalls",
      arguments: { query_model: { since, until, earliest: false, limit: 100 } },
    }),
  ]);

  // Teams
  const teamsData = teamsResult.status === "fulfilled" ? extract<any>(teamsResult.value) : null;
  const teams: Team[] = (teamsData?.response ?? []).map((t: any) => ({
    id: t.id,
    name: t.name ?? t.summary,
  }));

  // Service metrics
  const svcData = serviceResult.status === "fulfilled" ? extract<any>(serviceResult.value) : null;
  const serviceMetrics: ServiceMetric[] = (svcData?.response ?? []).map((s: any) => ({
    id: s.service_id ?? "",
    name: s.service_name ?? "Unknown",
    teamName: s.team_name ?? null,
    totalIncidents: s.total_incident_count ?? 0,
    mttaMinutes: secToMin(s.mean_seconds_to_first_ack),
    mttrMinutes: secToMin(s.mean_seconds_to_resolve),
    escalationCount: s.total_escalation_count ?? s.total_incidents_manual_escalated ?? 0,
    uptimePct: s.up_time_pct != null ? Math.round(s.up_time_pct * 10) / 10 : null,
  }));

  // Team metrics
  const teamData = teamResult.status === "fulfilled" ? extract<any>(teamResult.value) : null;
  const teamMetrics: TeamMetric[] = (teamData?.response ?? []).map((t: any) => ({
    id: t.team_id ?? "",
    name: t.team_name ?? "Unknown",
    totalIncidents: t.total_incident_count ?? 0,
    mttaMinutes: secToMin(t.mean_seconds_to_first_ack),
    mttrMinutes: secToMin(t.mean_seconds_to_resolve),
    escalationCount: t.total_escalation_count ?? t.total_incidents_manual_escalated ?? 0,
    totalInterruptions: t.total_interruptions ?? 0,
    uptimePct: t.up_time_pct != null ? Math.round(t.up_time_pct * 10) / 10 : null,
    businessHourInterruptions: t.total_business_hour_interruptions ?? 0,
    offHourInterruptions: t.total_off_hour_interruptions ?? 0,
    sleepHourInterruptions: t.total_sleep_hour_interruptions ?? 0,
    meanEngagedMinutes: secToMin(t.mean_engaged_seconds),
  }));

  // Build per-user oncall shifts from list_oncalls (clamped to [since, until])
  const oncallsData = oncallsResult.status === "fulfilled" ? extract<any>(oncallsResult.value) : null;
  const sinceMs = new Date(since).getTime();
  const untilMs = new Date(until).getTime();
  const userShifts = new Map<string, OncallShift[]>();
  for (const entry of (oncallsData?.response ?? [])) {
    const userId: string | undefined = entry.user?.id;
    if (!userId) continue;
    const rawStart = entry.start ? new Date(entry.start).getTime() : sinceMs;
    const rawEnd = entry.end ? new Date(entry.end).getTime() : untilMs;
    const s = Math.max(rawStart, sinceMs);
    const e = Math.min(rawEnd, untilMs);
    if (s >= e) continue;
    if (!userShifts.has(userId)) userShifts.set(userId, []);
    userShifts.get(userId)!.push({ userId, start: s, end: e });
  }

  // Responder metrics — get_responder_metrics returns one row per user+team.
  // Merge all team rows for the same user (max hours, sum interruptions/incidents).
  const respData = responderResult.status === "fulfilled" ? extract<any>(responderResult.value) : null;
  const mergedMap = new Map<string, {
    id: string; name: string; teamName: string | null; teamIds: string[];
    onCallHours: number; onCallHoursL1: number; onCallHoursL2Plus: number;
    totalIncidents: number; totalAcks: number; sleepInterruptions: number;
    engagedMinutes: number | null; totalInterruptions: number;
    businessHourInterruptions: number; offHourInterruptions: number;
    meanEngagedMinutes: number | null;
  }>();

  for (const r of (respData?.response ?? [])) {
    const userId: string = String(r.responder_id ?? "");
    if (!userId) continue;
    const onCallHours = secToHours(r.total_seconds_on_call);
    const onCallHoursL1 = secToHours(r.total_seconds_on_call_level_1);
    const onCallHoursL2Plus = secToHours(r.total_seconds_on_call_level_2_plus);
    const teamId: string | undefined = r.team_id ?? undefined;
    const teamName: string | undefined = r.team_name ?? undefined;

    const existing = mergedMap.get(userId);
    if (existing) {
      existing.onCallHours = Math.max(existing.onCallHours, onCallHours);
      existing.onCallHoursL1 = Math.max(existing.onCallHoursL1, onCallHoursL1);
      existing.onCallHoursL2Plus = Math.max(existing.onCallHoursL2Plus, onCallHoursL2Plus);
      existing.totalInterruptions += r.total_interruptions ?? 0;
      existing.businessHourInterruptions += r.total_business_hour_interruptions ?? 0;
      existing.offHourInterruptions += r.total_off_hour_interruptions ?? 0;
      existing.sleepInterruptions += r.total_sleep_hour_interruptions ?? 0;
      existing.totalIncidents += r.total_incident_count ?? 0;
      existing.totalAcks += r.total_incidents_acknowledged ?? 0;
      if (teamId && !existing.teamIds.includes(teamId)) existing.teamIds.push(teamId);
      if (teamName && !existing.teamName?.includes(teamName)) {
        existing.teamName = existing.teamName ? `${existing.teamName}, ${teamName}` : teamName;
      }
    } else {
      mergedMap.set(userId, {
        id: userId,
        name: r.responder_name ?? "Unknown",
        teamName: teamName ?? null,
        teamIds: teamId ? [teamId] : [],
        onCallHours,
        onCallHoursL1,
        onCallHoursL2Plus,
        totalIncidents: r.total_incident_count ?? 0,
        totalAcks: r.total_incidents_acknowledged ?? 0,
        sleepInterruptions: r.total_sleep_hour_interruptions ?? 0,
        engagedMinutes: secToMin(r.total_engaged_seconds),
        totalInterruptions: r.total_interruptions ?? 0,
        businessHourInterruptions: r.total_business_hour_interruptions ?? 0,
        offHourInterruptions: r.total_off_hour_interruptions ?? 0,
        meanEngagedMinutes: secToMin(r.mean_engaged_seconds),
      });
    }
  }

  const responderMetrics: ResponderMetric[] = Array.from(mergedMap.values()).map((r) => {
    const riskLevel = computeRisk(r.sleepInterruptions, r.engagedMinutes);
    return {
      ...r,
      riskLevel,
      oncallShifts: userShifts.get(r.id) ?? [],
    };
  });

  // Aggregated percentiles
  const aggRaw = aggregatedResult.status === "fulfilled" ? extract<any>(aggregatedResult.value) : null;
  const aggregated: AggregatedMetrics | null = aggRaw ? {
    p50AckSeconds: aggRaw.p50_seconds_to_first_ack ?? null,
    p75AckSeconds: aggRaw.p75_seconds_to_first_ack ?? null,
    p90AckSeconds: aggRaw.p90_seconds_to_first_ack ?? null,
    p95AckSeconds: aggRaw.p95_seconds_to_first_ack ?? null,
    p50ResolveSeconds: aggRaw.p50_seconds_to_resolve ?? null,
    p75ResolveSeconds: aggRaw.p75_seconds_to_resolve ?? null,
    p90ResolveSeconds: aggRaw.p90_seconds_to_resolve ?? null,
    p95ResolveSeconds: aggRaw.p95_seconds_to_resolve ?? null,
  } : null;

  // Trends — weekly rollup, group rows by week and sum across teams
  const trendsRaw = trendsResult.status === "fulfilled" ? extract<any>(trendsResult.value) : null;
  const trendsData: TrendsData | null = trendsRaw ? (() => {
    const byWeek = new Map<string, { totalIncidents: number; mttaSum: number; mttrSum: number; intSum: number; mttaCount: number; mttrCount: number }>();
    for (const row of (trendsRaw.response ?? [])) {
      const week = (row.range_start ?? "").substring(0, 10);
      if (!week) continue;
      const existing = byWeek.get(week) ?? { totalIncidents: 0, mttaSum: 0, mttrSum: 0, intSum: 0, mttaCount: 0, mttrCount: 0 };
      const inc = row.total_incident_count ?? 0;
      existing.totalIncidents += inc;
      existing.intSum += row.total_interruptions ?? 0;
      if (row.mean_seconds_to_first_ack != null && inc > 0) {
        existing.mttaSum += row.mean_seconds_to_first_ack * inc;
        existing.mttaCount += inc;
      }
      if (row.mean_seconds_to_resolve != null && inc > 0) {
        existing.mttrSum += row.mean_seconds_to_resolve * inc;
        existing.mttrCount += inc;
      }
      byWeek.set(week, existing);
    }
    const points: TrendPoint[] = Array.from(byWeek.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([weekStart, v]) => ({
        weekStart,
        totalIncidents: v.totalIncidents,
        mttaMinutes: v.mttaCount > 0 ? Math.round(v.mttaSum / v.mttaCount / 60) : null,
        mttrMinutes: v.mttrCount > 0 ? Math.round(v.mttrSum / v.mttrCount / 60) : null,
        totalInterruptions: v.intSum,
      }));
    return { points };
  })() : null;

  // KPI summary — aggregate across all returned teams
  const totalIncidents = teamMetrics.reduce((s, t) => s + t.totalIncidents, 0);
  const totalEscalations = teamMetrics.reduce((s, t) => s + t.escalationCount, 0);
  // Weighted average: weight each team's mean by its incident count
  function weightedAvg(teams: TeamMetric[], getter: (t: TeamMetric) => number | null): number | null {
    const valid = teams.filter((t) => getter(t) !== null && t.totalIncidents > 0);
    if (valid.length === 0) return null;
    const totalWeight = valid.reduce((s, t) => s + t.totalIncidents, 0);
    return Math.round(valid.reduce((s, t) => s + getter(t)! * t.totalIncidents, 0) / totalWeight);
  }

  // uptime: average across services (more meaningful than teams)
  const uptimeValues = serviceMetrics.map((s) => s.uptimePct).filter((v): v is number => v !== null);
  const uptimePct = uptimeValues.length > 0
    ? Math.round((uptimeValues.reduce((a, b) => a + b, 0) / uptimeValues.length) * 10) / 10
    : null;

  return {
    teams,
    selectedTeam: teamId,
    since,
    until,
    totalIncidents,
    mttaMinutes: weightedAvg(teamMetrics, (t) => t.mttaMinutes),
    mttrMinutes: weightedAvg(teamMetrics, (t) => t.mttrMinutes),
    escalationRate: totalIncidents > 0 ? Math.round((totalEscalations / totalIncidents) * 100) : null,
    uptimePct,
    aggregated,
    trendsData,
    serviceMetrics,
    teamMetrics,
    responderMetrics,
  };
}

