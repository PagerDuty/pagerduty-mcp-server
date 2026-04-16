/**
 * Operations Intelligence - API layer
 * Fetches incident + service + oncall data for operational health dashboard.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Team {
  id: string;
  name: string;
}

export interface ServiceStat {
  id: string;
  name: string;
  incidentCount: number;
  highUrgencyCount: number;
  mttrMinutes: number | null; // null if no resolved incidents
}

export interface OpsData {
  teams: Team[];
  selectedTeam: string | null;
  since: string;
  until: string;
  totalIncidents: number;
  highUrgencyCount: number;
  resolvedCount: number;
  mttrMinutes: number | null;
  serviceStats: ServiceStat[];
  recentIncidents: RecentIncident[];
  oncallUsers: string[];
}

export interface RecentIncident {
  id: string;
  number: number;
  title: string;
  status: string;
  urgency: string;
  serviceName: string;
  createdAt: string;
  resolvedAt: string | null;
  mttrMinutes: number | null;
  priority: string | null;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function mttr(start: string, end: string | null): number | null {
  if (!end) return null;
  return Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
}

// ─── API functions ────────────────────────────────────────────────────────────

export async function fetchOpsData(
  app: App,
  since: string,
  until: string,
  teamId: string | null
): Promise<OpsData> {
  // Build teams query first to return in result
  const teamsResult = await app.callServerTool({
    name: "list_teams",
    arguments: { query_model: { limit: 100 } },
  });
  const teamsData = extract<any>(teamsResult);
  const teams: Team[] = (teamsData?.response ?? []).map((t: any) => ({
    id: t.id,
    name: t.name ?? t.summary,
  }));

  // Fetch incidents (optionally filtered by team)
  const incArgs: any = {
    query_model: {
      status: ["triggered", "acknowledged", "resolved"],
      since,
      until,
      limit: 100,
    },
  };
  if (teamId) incArgs.query_model.team_ids = [teamId];

  const [incResult, oncallResult] = await Promise.allSettled([
    app.callServerTool({ name: "list_incidents", arguments: incArgs }),
    app.callServerTool({
      name: "list_oncalls",
      arguments: {
        query_model: {
          since,
          until,
          earliest: true,
        },
      },
    }),
  ]);

  const incidents: any[] = incResult.status === "fulfilled"
    ? (extract<any>(incResult.value)?.response ?? []) : [];

  const oncalls: any[] = oncallResult.status === "fulfilled"
    ? (extract<any>(oncallResult.value)?.response ?? []) : [];

  // Compute stats
  const resolved = incidents.filter((i: any) => i.status === "resolved");
  const highUrgency = incidents.filter((i: any) => i.urgency === "high");

  // MTTR
  const mttrValues = resolved
    .map((i: any) => mttr(i.created_at, i.resolved_at))
    .filter((v): v is number => v !== null);
  const avgMttr = mttrValues.length > 0
    ? Math.round(mttrValues.reduce((a, b) => a + b, 0) / mttrValues.length)
    : null;

  // Service breakdown
  const serviceMap = new Map<string, ServiceStat>();
  for (const inc of incidents) {
    const svcId = inc.service?.id ?? "unknown";
    const svcName = inc.service?.summary ?? "Unknown";
    if (!serviceMap.has(svcId)) {
      serviceMap.set(svcId, { id: svcId, name: svcName, incidentCount: 0, highUrgencyCount: 0, mttrMinutes: null });
    }
    const stat = serviceMap.get(svcId)!;
    stat.incidentCount++;
    if (inc.urgency === "high") stat.highUrgencyCount++;
  }
  // MTTR per service
  for (const inc of resolved) {
    const svcId = inc.service?.id ?? "unknown";
    const stat = serviceMap.get(svcId);
    if (stat) {
      const m = mttr(inc.created_at, inc.resolved_at);
      if (m !== null) {
        stat.mttrMinutes = stat.mttrMinutes === null ? m : Math.round((stat.mttrMinutes + m) / 2);
      }
    }
  }
  const serviceStats = [...serviceMap.values()].sort((a, b) => b.incidentCount - a.incidentCount);

  // Recent incidents
  const recentIncidents: RecentIncident[] = incidents.slice(0, 50).map((i: any) => ({
    id: i.id,
    number: i.incident_number,
    title: i.title ?? i.summary,
    status: i.status,
    urgency: i.urgency,
    serviceName: i.service?.summary ?? "Unknown",
    createdAt: i.created_at,
    resolvedAt: i.resolved_at ?? null,
    mttrMinutes: mttr(i.created_at, i.resolved_at),
    priority: i.priority?.summary ?? null,
  }));

  // On-call users (unique)
  const oncallUserSet = new Set<string>();
  for (const oc of oncalls) {
    if (oc.user?.summary) oncallUserSet.add(oc.user.summary);
  }

  return {
    teams,
    selectedTeam: teamId,
    since,
    until,
    totalIncidents: incidents.length,
    highUrgencyCount: highUrgency.length,
    resolvedCount: resolved.length,
    mttrMinutes: avgMttr,
    serviceStats,
    recentIncidents,
    oncallUsers: [...oncallUserSet].slice(0, 10),
  };
}
