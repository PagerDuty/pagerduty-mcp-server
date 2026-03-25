/**
 * API functions for Oncall Compensation Report
 *
 * Primary metrics (oncall hours, interruptions) come from PagerDuty Analytics
 * via get_responder_metrics. Raw on-call shift windows come from list_oncalls
 * and are used to compute the outside-business-hours metrics in the browser.
 * Individual incident records come from list_incidents for the per-user detail modal.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import type { OncallShift } from "./businessHours";

export type { OncallShift };

export interface IncidentRecord {
  id: string;
  incidentNumber: number;
  title: string;
  urgency: "high" | "low";
  createdAt: string;
  resolvedAt: string;
  durationHours: number;
  serviceName?: string;
}

export interface UserCompensationRecord {
  userId: string;
  userName: string;
  teamId?: string;
  teamName?: string;

  // Oncall hours — from Analytics (authoritative)
  scheduledHours: number;       // total_seconds_on_call / 3600
  scheduledHoursL1: number;     // total_seconds_on_call_level_1 / 3600
  scheduledHoursL2Plus: number; // total_seconds_on_call_level_2_plus / 3600

  // Incident metrics — from Analytics
  incidentCount: number;        // total_incident_count
  incidentHours: number;        // total_engaged_seconds / 3600
  interruptionRate: number;     // total_interruptions / scheduledHours

  // Interruption breakdown — from Analytics (PagerDuty native categories)
  totalInterruptions: number;
  businessHourInterruptions: number;
  offHourInterruptions: number;
  sleepHourInterruptions: number;
  meanTimeToAckSeconds: number;

  // High/low urgency — derived from list_incidents
  highUrgencyCount: number;
  lowUrgencyCount: number;

  // Individual incident records — for modal detail
  incidents: IncidentRecord[];

  // Raw on-call shift windows — used to compute outside hours metrics
  oncallShifts: OncallShift[];

  // Outside business hours metrics — computed in the browser from oncallShifts + config
  // Default to 0; recomputed whenever BusinessHoursConfig changes
  outsideHours: number;
  weekendHours: number;
  holidayHours: number;
  maxConsecutiveOutsideHours: number;
  uniquePeriodsOutside: number;
}

export interface TeamInfo {
  id: string;
  name: string;
}

export interface CompensationData {
  records: UserCompensationRecord[];
  teams: TeamInfo[];
  since: string;
  until: string;
}

// Cap incident duration to avoid outliers
const MAX_INCIDENT_HOURS = 24;

function extractData<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function diffHours(start: string, end: string): number {
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return Math.max(0, ms / 3_600_000);
}

export async function fetchCompensationData(
  app: App,
  since: string,
  until: string,
): Promise<CompensationData> {
  const [metricsResult, incidentsResult, teamsResult, oncallsResult] =
    await Promise.allSettled([
      app.callServerTool({
        name: "get_responder_metrics",
        arguments: {
          request: {
            filters: {
              date_range_start: since,
              date_range_end: until,
            },
          },
        },
      }),
      app.callServerTool({
        name: "list_incidents",
        arguments: {
          query_model: {
            status: ["triggered", "acknowledged", "resolved"],
            since,
            until,
            limit: 1000,
          },
        },
      }),
      app.callServerTool({
        name: "list_teams",
        arguments: { query_model: { limit: 100 } },
      }),
      app.callServerTool({
        name: "list_oncalls",
        arguments: {
          query_model: {
            since,
            until,
            earliest: false,
            limit: 100,
          },
        },
      }),
    ]);

  const metricsData =
    metricsResult.status === "fulfilled"
      ? extractData<any>(metricsResult.value)
      : null;
  const incidentsData =
    incidentsResult.status === "fulfilled"
      ? extractData<any>(incidentsResult.value)
      : null;
  const teamsData =
    teamsResult.status === "fulfilled"
      ? extractData<any>(teamsResult.value)
      : null;
  const oncallsData =
    oncallsResult.status === "fulfilled"
      ? extractData<any>(oncallsResult.value)
      : null;

  // Build teams map: id → name
  const teamsMap = new Map<string, string>();
  const teamsArray: TeamInfo[] = [];
  for (const t of teamsData?.response ?? []) {
    const name: string = t.name ?? t.summary ?? "Unknown Team";
    teamsMap.set(t.id as string, name);
    teamsArray.push({ id: t.id as string, name });
  }

  // Build per-user oncall shifts from list_oncalls
  // Clamp shift windows to [since, until] to avoid processing data outside the range.
  const sinceMs = new Date(since).getTime();
  const untilMs = new Date(until).getTime();
  const userShifts = new Map<string, OncallShift[]>();

  for (const entry of oncallsData?.response ?? []) {
    const userId: string | undefined = entry.user?.id;
    if (!userId) continue;

    const rawStart = entry.start ? new Date(entry.start).getTime() : sinceMs;
    const rawEnd = entry.end ? new Date(entry.end).getTime() : untilMs;

    const start = Math.max(rawStart, sinceMs);
    const end = Math.min(rawEnd, untilMs);
    if (start >= end) continue;

    if (!userShifts.has(userId)) userShifts.set(userId, []);
    userShifts.get(userId)!.push({ userId, start, end });
  }

  // Group incidents by assigned user for detail modal + urgency counts
  const userIncidents = new Map<string, IncidentRecord[]>();

  for (const inc of incidentsData?.response ?? []) {
    const assignments: any[] = inc.assignments ?? [];
    const assigneeIds: string[] = assignments
      .map((a: any) => a.assignee?.id as string | undefined)
      .filter((id): id is string => !!id);

    const createdAt: string = inc.created_at ?? "";
    const resolvedAt: string = inc.resolved_at ?? "";
    const rawDuration = createdAt && resolvedAt ? diffHours(createdAt, resolvedAt) : 0;
    const durationHours = Number(Math.min(MAX_INCIDENT_HOURS, rawDuration).toFixed(2));

    const record: IncidentRecord = {
      id: inc.id as string,
      incidentNumber: inc.incident_number as number,
      title: (inc.title as string | undefined) ?? "Untitled Incident",
      urgency: inc.urgency === "high" ? "high" : "low",
      createdAt,
      resolvedAt,
      durationHours,
      serviceName: inc.service?.summary as string | undefined,
    };

    const seen = new Set<string>();
    for (const uid of assigneeIds) {
      if (seen.has(uid)) continue;
      seen.add(uid);
      if (!userIncidents.has(uid)) userIncidents.set(uid, []);
      userIncidents.get(uid)!.push(record);
    }
  }

  // Build final records from analytics data
  const records: UserCompensationRecord[] = [];

  for (const m of metricsData?.response ?? []) {
    const userId: string = String(m.responder_id ?? "");
    if (!userId) continue;

    const scheduledHours = Number(((m.total_seconds_on_call ?? 0) / 3600).toFixed(2));
    const scheduledHoursL1 = Number(((m.total_seconds_on_call_level_1 ?? 0) / 3600).toFixed(2));
    const scheduledHoursL2Plus = Number(((m.total_seconds_on_call_level_2_plus ?? 0) / 3600).toFixed(2));

    const totalInterruptions = m.total_interruptions ?? 0;
    const businessHourInterruptions = m.total_business_hour_interruptions ?? 0;
    const offHourInterruptions = m.total_off_hour_interruptions ?? 0;
    const sleepHourInterruptions = m.total_sleep_hour_interruptions ?? 0;
    const incidentHours = Number(((m.total_engaged_seconds ?? 0) / 3600).toFixed(2));
    const incidentCount = m.total_incident_count ?? 0;
    const meanTimeToAckSeconds = m.mean_time_to_acknowledge_seconds ?? 0;
    const interruptionRate =
      scheduledHours > 0
        ? Number((totalInterruptions / scheduledHours).toFixed(3))
        : 0;

    const teamId: string | undefined = m.team_id ?? undefined;
    const teamName: string | undefined =
      (teamId ? teamsMap.get(teamId) : undefined) ?? m.team_name ?? undefined;

    const incidents = userIncidents.get(userId) ?? [];
    const highUrgencyCount = incidents.filter((i) => i.urgency === "high").length;
    const lowUrgencyCount = incidents.filter((i) => i.urgency === "low").length;
    const oncallShifts = userShifts.get(userId) ?? [];

    records.push({
      userId,
      userName: m.responder_name ?? "Unknown User",
      teamId,
      teamName,
      scheduledHours,
      scheduledHoursL1,
      scheduledHoursL2Plus,
      incidentCount,
      incidentHours,
      interruptionRate,
      totalInterruptions,
      businessHourInterruptions,
      offHourInterruptions,
      sleepHourInterruptions,
      meanTimeToAckSeconds,
      highUrgencyCount,
      lowUrgencyCount,
      incidents,
      oncallShifts,
      // Outside hours default to 0 — computed in the app via useMemo
      outsideHours: 0,
      weekendHours: 0,
      holidayHours: 0,
      maxConsecutiveOutsideHours: 0,
      uniquePeriodsOutside: 0,
    });
  }

  // Default sort: highest scheduled hours first
  records.sort((a, b) => b.scheduledHours - a.scheduledHours);

  return { records, teams: teamsArray, since, until };
}
