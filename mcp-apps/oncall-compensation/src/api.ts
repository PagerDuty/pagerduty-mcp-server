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

export interface EscalationPolicyInfo {
  id: string;
  name: string;
}

export interface UserCompensationRecord {
  userId: string;
  userName: string;
  userTimezone?: string;
  teamId?: string;
  teamIds: string[];
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
  hasScheduleShifts: boolean; // true if any shift is backed by a schedule (not directly added)

  // Outside business hours metrics — computed in the browser from oncallShifts + config
  // Default to 0; recomputed whenever BusinessHoursConfig changes
  outsideHours: number;
  weekendHours: number;
  holidayHours: number;
  maxConsecutiveOutsideHours: number;
  uniquePeriodsOutside: number;
  weekendPeriodCount: number;
  holidayCount: number;
  maxConsecutiveOnCallDays: number;
  maxConsecutiveOnCallHours: number;
  minRestHours: number;

  // Estimated compensation — computed in the browser from PayConfig
  // Default to 0; recomputed whenever PayConfig changes
  estimatedPay: number;
}

export interface TeamInfo {
  id: string;
  name: string;
}

export interface CompensationData {
  records: UserCompensationRecord[];
  teams: TeamInfo[];
  escalationPolicies: EscalationPolicyInfo[];
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
  escalationPolicyId?: string,
): Promise<CompensationData> {
  const oncallsArgs: Record<string, unknown> = {
    since,
    until,
    earliest: false,
    limit: 100,
  };
  if (escalationPolicyId) {
    oncallsArgs.escalation_policy_ids = [escalationPolicyId];
  }

  const [metricsResult, incidentsResult, teamsResult, oncallsResult, epResult, usersResult] =
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
        arguments: { query_model: oncallsArgs },
      }),
      app.callServerTool({
        name: "list_escalation_policies",
        arguments: { query_model: { limit: 100 } },
      }),
      app.callServerTool({
        name: "list_users",
        arguments: { query_model: { limit: 100 } },
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
  const epData =
    epResult.status === "fulfilled"
      ? extractData<any>(epResult.value)
      : null;
  const usersData =
    usersResult.status === "fulfilled"
      ? extractData<any>(usersResult.value)
      : null;

  // Build teams map: id → name
  const teamsMap = new Map<string, string>();
  const teamsArray: TeamInfo[] = [];
  for (const t of teamsData?.response ?? []) {
    const name: string = t.name ?? t.summary ?? "Unknown Team";
    teamsMap.set(t.id as string, name);
    teamsArray.push({ id: t.id as string, name });
  }

  // Build escalation policies list
  const escalationPolicies: EscalationPolicyInfo[] = [];
  for (const ep of epData?.response ?? []) {
    if (ep.id && ep.name) {
      escalationPolicies.push({ id: ep.id as string, name: ep.name as string });
    }
  }
  escalationPolicies.sort((a, b) => a.name.localeCompare(b.name));

  // Build user timezone map: userId → IANA timezone
  const userTimezoneMap = new Map<string, string>();
  for (const u of usersData?.response ?? []) {
    if (u.id && u.time_zone) {
      userTimezoneMap.set(u.id as string, u.time_zone as string);
    }
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

    const hasSchedule = !!entry.schedule?.id;
    if (!userShifts.has(userId)) userShifts.set(userId, []);
    userShifts.get(userId)!.push({ userId, start, end, hasSchedule });
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

  // Build final records from analytics data.
  // get_responder_metrics returns one entry per user per team, so we merge
  // all team rows for the same user into a single record:
  //   - hours: take the max (same schedule repeated across teams, not additive)
  //   - interruptions/incidents: sum across teams (team-scoped counts)
  //   - teams: collect all team names
  const mergedMap = new Map<string, UserCompensationRecord>();

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

    const teamId: string | undefined = m.team_id ?? undefined;
    const teamName: string | undefined =
      (teamId ? teamsMap.get(teamId) : undefined) ?? m.team_name ?? undefined;

    const existing = mergedMap.get(userId);
    if (existing) {
      // Merge: max hours, sum interruptions/incidents, append team name
      existing.scheduledHours = Math.max(existing.scheduledHours, scheduledHours);
      existing.scheduledHoursL1 = Math.max(existing.scheduledHoursL1, scheduledHoursL1);
      existing.scheduledHoursL2Plus = Math.max(existing.scheduledHoursL2Plus, scheduledHoursL2Plus);
      existing.totalInterruptions += totalInterruptions;
      existing.businessHourInterruptions += businessHourInterruptions;
      existing.offHourInterruptions += offHourInterruptions;
      existing.sleepHourInterruptions += sleepHourInterruptions;
      existing.incidentCount += incidentCount;
      existing.incidentHours = Number((existing.incidentHours + incidentHours).toFixed(2));
      if (meanTimeToAckSeconds > 0 && existing.meanTimeToAckSeconds === 0) {
        existing.meanTimeToAckSeconds = meanTimeToAckSeconds;
      }
      if (teamId && !existing.teamIds.includes(teamId)) {
        existing.teamIds.push(teamId);
      }
      if (teamName && !existing.teamName?.includes(teamName)) {
        existing.teamName = existing.teamName ? `${existing.teamName}, ${teamName}` : teamName;
      }
    } else {
      const incidents = userIncidents.get(userId) ?? [];
      const highUrgencyCount = incidents.filter((i) => i.urgency === "high").length;
      const lowUrgencyCount = incidents.filter((i) => i.urgency === "low").length;
      const oncallShifts = userShifts.get(userId) ?? [];
      const hasScheduleShifts = oncallShifts.some((s) => s.hasSchedule);
      const interruptionRate =
        scheduledHours > 0
          ? Number((totalInterruptions / scheduledHours).toFixed(3))
          : 0;

      mergedMap.set(userId, {
        userId,
        userName: m.responder_name ?? "Unknown User",
        userTimezone: userTimezoneMap.get(userId),
        teamId,
        teamIds: teamId ? [teamId] : [],
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
        hasScheduleShifts,
        outsideHours: 0,
        weekendHours: 0,
        holidayHours: 0,
        maxConsecutiveOutsideHours: 0,
        uniquePeriodsOutside: 0,
        weekendPeriodCount: 0,
        holidayCount: 0,
        maxConsecutiveOnCallDays: 0,
        maxConsecutiveOnCallHours: 0,
        minRestHours: 999,
        estimatedPay: 0,
      });
    }
  }

  // Recalculate interruptionRate after all team rows are merged
  let records: UserCompensationRecord[] = Array.from(mergedMap.values()).map((r) => ({
    ...r,
    interruptionRate:
      r.scheduledHours > 0
        ? Number((r.totalInterruptions / r.scheduledHours).toFixed(3))
        : 0,
  }));

  // When an EP filter is active, restrict to users who appeared in the EP-filtered oncalls
  if (escalationPolicyId) {
    const epUserIds = new Set<string>();
    for (const entry of oncallsData?.response ?? []) {
      const uid: string | undefined = entry.user?.id;
      if (uid) epUserIds.add(uid);
    }
    records = records.filter((r) => epUserIds.has(r.userId));
  }

  // Default sort: highest scheduled hours first
  records.sort((a, b) => b.scheduledHours - a.scheduledHours);

  return { records, teams: teamsArray, escalationPolicies, since, until };
}
