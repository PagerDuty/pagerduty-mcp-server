/**
 * Operations Intelligence v2 - API layer
 *
 * Fetches pre-aggregated metrics from PagerDuty Analytics API tools.
 * No raw incident list — all metrics are server-side aggregated.
 *
 * Insights tab calls insights_agent_tool via app.callServerTool.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

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
}

export interface ResponderMetric {
  id: string;
  name: string;
  teamName: string | null;
  onCallHours: number;              // total_seconds_on_call / 3600
  totalIncidents: number;
  totalAcks: number;
  sleepInterruptions: number;
  engagedMinutes: number | null;    // total_engaged_seconds / 60
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
  // Section data
  serviceMetrics: ServiceMetric[];
  teamMetrics: TeamMetric[];
  responderMetrics: ResponderMetric[];
}

export interface InsightMessage {
  role: "user" | "assistant";
  content: string;
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
  const incidentFilters = buildIncidentFilters(since, until, teamId);
  // Responder endpoint uses date_range_start/end (different field names)
  const responderFilters: Record<string, unknown> = {
    date_range_start: since,
    date_range_end: until,
  };
  if (teamId) responderFilters["team_ids"] = [teamId];

  const [teamsResult, serviceResult, teamResult, responderResult] = await Promise.allSettled([
    app.callServerTool({ name: "list_teams", arguments: { query_model: { limit: 100 } } }),
    app.callServerTool({
      name: "get_incident_metrics_by_service",
      arguments: { filters: incidentFilters },
    }),
    app.callServerTool({
      name: "get_incident_metrics_by_team",
      arguments: { filters: incidentFilters },
    }),
    app.callServerTool({
      name: "get_responder_load_metrics",
      arguments: { filters: responderFilters },
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
    uptimePct: s.up_time_pct ?? null,
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
    uptimePct: t.up_time_pct ?? null,
  }));

  // Responder metrics
  const respData = responderResult.status === "fulfilled" ? extract<any>(responderResult.value) : null;
  const responderMetrics: ResponderMetric[] = (respData?.response ?? []).map((r: any) => ({
    id: r.responder_id ?? "",
    name: r.responder_name ?? "Unknown",
    teamName: r.team_name ?? null,
    onCallHours: secToHours(r.total_seconds_on_call),
    totalIncidents: r.total_incident_count ?? 0,
    totalAcks: r.total_incidents_acknowledged ?? 0,
    sleepInterruptions: r.total_sleep_hour_interruptions ?? 0,
    engagedMinutes: secToMin(r.total_engaged_seconds),
  }));

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
    serviceMetrics,
    teamMetrics,
    responderMetrics,
  };
}

// ─── Insights fetch (PagerDuty Advanced MCP) ─────────────────────────────────

export async function fetchInsight(
  app: App,
  message: string,
  sessionId: string
): Promise<string> {
  const result = await app.callServerTool({
    name: "insights_agent_tool",
    arguments: { message, session_id: sessionId },
  });
  const data = extract<{ message: string }>(result);
  return data?.message ?? "";
}
