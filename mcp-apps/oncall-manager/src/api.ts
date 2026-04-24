import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
}

export interface Schedule {
  id: string;
  name: string;
  timeZone: string;
}

export interface ScheduleLayer {
  id: string;
  name: string;
  rotationSeconds: number;
  rotationVirtualStart: string;
  start: string;
  end: string | null;
  restrictions: any[] | null;
  users: ScheduleUser[];
}

export interface ScheduleDetail {
  id: string;
  name: string;
  description: string | null;
  timeZone: string;
  layers: ScheduleLayer[];
  allUsers: ScheduleUser[];
}

export interface OnCallShift {
  scheduleId: string;
  scheduleName: string;
  userId: string;
  userName: string;
  start: string;
  end: string;
  escalationLevel: number;
}

export interface OverrideDetail {
  id: string;
  scheduleId: string;
  scheduleName: string;
  start: string;
  end: string;
  user: { id: string; name: string };
}

export interface ScheduleUser {
  id: string;
  name: string;
  email: string;
}

export interface EscalationTarget {
  id: string;
  type: "user_reference" | "schedule_reference";
  summary: string;
}

export interface EscalationRule {
  id?: string;
  escalation_delay_in_minutes: number;
  targets: EscalationTarget[];
}

export interface EscalationPolicy {
  id: string;
  name: string;
  description: string | null;
  num_loops: number;
  escalation_rules: EscalationRule[];
  services: Array<{ id: string; summary: string }>;
  teams: Array<{ id: string; summary: string }>;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

// ─── Current user ─────────────────────────────────────────────────────────────

export async function fetchCurrentUser(app: App): Promise<CurrentUser | null> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.currentUser;
  }
  const result = await app.callServerTool({ name: "get_user_data", arguments: {} });
  const data = extract<any>(result);
  const user = data?.response ?? data;
  if (!user?.id) return null;
  return { id: user.id, name: user.name, email: user.email };
}

// ─── Schedules ────────────────────────────────────────────────────────────────

export async function fetchSchedules(app: App): Promise<Schedule[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.schedules;
  }
  const result = await app.callServerTool({
    name: "list_schedules",
    arguments: { query_model: { limit: 100 } },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((s: any) => ({
    id: s.id,
    name: s.name ?? s.summary,
    timeZone: s.time_zone ?? "UTC",
  }));
}

export async function fetchScheduleDetail(app: App, scheduleId: string): Promise<ScheduleDetail | null> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.scheduleDetails[scheduleId] ?? null;
  }
  const result = await app.callServerTool({
    name: "get_schedule",
    arguments: { schedule_id: scheduleId },
  });
  const data = extract<any>(result);
  const s = data?.schedule ?? data;
  if (!s?.id) return null;

  const layers: ScheduleLayer[] = (s.schedule_layers ?? []).map((l: any) => ({
    id: l.id,
    name: l.name,
    rotationSeconds: l.rotation_turn_length_seconds ?? 604800,
    rotationVirtualStart: l.rotation_virtual_start,
    start: l.start,
    end: l.end ?? null,
    restrictions: l.restrictions ?? null,
    users: (l.users ?? []).map((lu: any) => ({
      id: lu.user?.id ?? lu.id,
      name: lu.user?.summary ?? lu.user?.name ?? "Unknown",
      email: lu.user?.email ?? "",
    })),
  }));

  const allUsers: ScheduleUser[] = (s.users ?? []).map((u: any) => ({
    id: u.id,
    name: u.name ?? u.summary,
    email: u.email ?? "",
  }));

  return {
    id: s.id,
    name: s.name,
    description: s.description ?? null,
    timeZone: s.time_zone ?? "UTC",
    layers,
    allUsers,
  };
}

export async function saveScheduleDetail(
  app: App,
  scheduleDetail: ScheduleDetail,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "update_schedule",
    arguments: {
      schedule_id: scheduleDetail.id,
      update_model: {
        schedule: {
          name: scheduleDetail.name,
          time_zone: scheduleDetail.timeZone,
          description: scheduleDetail.description,
          type: "schedule",
          schedule_layers: scheduleDetail.layers.map((l) => ({
            name: l.name,
            start: l.start,
            end: l.end ?? undefined,
            rotation_virtual_start: l.rotationVirtualStart,
            rotation_turn_length_seconds: l.rotationSeconds,
            users: l.users.map((u) => ({
              user: { id: u.id, type: "user_reference" },
            })),
            restrictions: l.restrictions ?? undefined,
          })),
        },
      },
    },
  });
  return !result.isError;
}

// ─── On-calls ─────────────────────────────────────────────────────────────────

export async function fetchUserShifts(
  app: App,
  userId: string,
  since: string,
  until: string,
): Promise<OnCallShift[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.myShifts;
  }
  const result = await app.callServerTool({
    name: "list_oncalls",
    arguments: {
      query_model: { user_ids: [userId], since, until, earliest: false },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end && o.user?.id)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
      userId: o.user.id,
      userName: o.user.summary ?? o.user.name ?? "Unknown",
      start: o.start,
      end: o.end,
      escalationLevel: o.escalation_level ?? 0,
    }));
}

export async function fetchAllOnCalls(
  app: App,
  since: string,
  until: string,
): Promise<OnCallShift[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.allShifts;
  }
  const result = await app.callServerTool({
    name: "list_oncalls",
    arguments: { query_model: { since, until, earliest: false } },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end && o.user?.id)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
      userId: o.user.id,
      userName: o.user.summary ?? o.user.name ?? "Unknown",
      start: o.start,
      end: o.end,
      escalationLevel: o.escalation_level ?? 0,
    }));
}

// ─── Overrides ────────────────────────────────────────────────────────────────

export async function fetchScheduleOverrides(
  app: App,
  scheduleId: string,
  since: string,
  until: string,
): Promise<OverrideDetail[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return (MOCK_ONCALL_DATA.overridesBySchedule[scheduleId] ?? []).map((o) => ({
      ...o,
      scheduleId,
      scheduleName: MOCK_ONCALL_DATA.schedules.find((s) => s.id === scheduleId)?.name ?? scheduleId,
    }));
  }
  const result = await app.callServerTool({
    name: "list_schedule_overrides",
    arguments: { schedule_id: scheduleId, since, until },
  });
  const data = extract<any>(result);
  const items: any[] = data?.overrides ?? [];
  return items.map((o: any) => ({
    id: o.id,
    scheduleId,
    scheduleName: "",
    start: o.start,
    end: o.end,
    user: { id: o.user?.id ?? "", name: o.user?.name ?? o.user?.summary ?? "Unknown" },
  }));
}

export async function deleteOverride(
  app: App,
  scheduleId: string,
  overrideId: string,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "delete_schedule_override",
    arguments: { schedule_id: scheduleId, override_id: overrideId },
  });
  return !result.isError;
}

export async function createOverride(
  app: App,
  scheduleId: string,
  userId: string,
  start: string,
  end: string,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "create_schedule_override",
    arguments: {
      schedule_id: scheduleId,
      override_request: {
        overrides: [{ start, end, user: { id: userId, type: "user_reference" } }],
      },
    },
  });
  return !result.isError;
}

// ─── Schedule users (with fallback) ──────────────────────────────────────────

export async function fetchScheduleUsers(
  app: App,
  scheduleId: string,
): Promise<ScheduleUser[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.scheduleUsers[scheduleId] ?? [];
  }
  const result = await app.callServerTool({
    name: "list_schedule_users",
    arguments: { schedule_id: scheduleId },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  if (items.length > 0) {
    return items.map((u: any) => ({
      id: u.id,
      name: u.name ?? u.summary,
      email: u.email ?? "",
    }));
  }
  // Fallback: extract unique users from list_oncalls for this schedule
  const since = new Date().toISOString();
  const until = new Date(Date.now() + 30 * 86_400_000).toISOString();
  const fallback = await app.callServerTool({
    name: "list_oncalls",
    arguments: {
      query_model: { schedule_ids: [scheduleId], since, until, earliest: false },
    },
  });
  const fallbackData = extract<any>(fallback);
  const fallbackItems: any[] = fallbackData?.response ?? [];
  const seen = new Set<string>();
  const users: ScheduleUser[] = [];
  for (const o of fallbackItems) {
    if (o.user?.id && !seen.has(o.user.id)) {
      seen.add(o.user.id);
      users.push({
        id: o.user.id,
        name: o.user.summary ?? o.user.name ?? "Unknown",
        email: o.user.email ?? "",
      });
    }
  }
  return users;
}

// ─── All users (for adding to schedules / EP targets) ────────────────────────

export async function fetchUsers(app: App, query?: string): Promise<ScheduleUser[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    const all = MOCK_ONCALL_DATA.allUsers;
    if (!query) return all;
    const q = query.toLowerCase();
    return all.filter((u) => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
  }
  const args: any = { query_model: { limit: 100 } };
  if (query) args.query_model.query = query;
  const result = await app.callServerTool({ name: "list_users", arguments: args });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((u: any) => ({
    id: u.id,
    name: u.name ?? u.summary,
    email: u.email ?? "",
  }));
}

// ─── Escalation policies ─────────────────────────────────────────────────────

export async function fetchEscalationPolicies(
  app: App,
  query?: string,
): Promise<EscalationPolicy[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    const all = MOCK_ONCALL_DATA.escalationPolicies;
    if (!query) return all;
    const q = query.toLowerCase();
    return all.filter((p) => p.name.toLowerCase().includes(q));
  }
  const args: any = { query_model: { limit: 100, include: ["services", "teams"] } };
  if (query) args.query_model.query = query;
  const result = await app.callServerTool({
    name: "list_escalation_policies",
    arguments: args,
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map(mapEscalationPolicy);
}

export async function fetchEscalationPolicy(
  app: App,
  policyId: string,
): Promise<EscalationPolicy | null> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.escalationPolicies.find((p) => p.id === policyId) ?? null;
  }
  const result = await app.callServerTool({
    name: "get_escalation_policy",
    arguments: { policy_id: policyId },
  });
  const data = extract<any>(result);
  if (!data?.id) return null;
  return mapEscalationPolicy(data);
}

export async function updateEscalationPolicy(
  app: App,
  policyId: string,
  policy: Pick<EscalationPolicy, "name" | "description" | "num_loops" | "escalation_rules">,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "update_escalation_policy",
    arguments: {
      policy_id: policyId,
      escalation_policy: {
        name: policy.name,
        description: policy.description,
        num_loops: policy.num_loops,
        escalation_rules: policy.escalation_rules.map((r) => ({
          escalation_delay_in_minutes: r.escalation_delay_in_minutes,
          targets: r.targets.map((t) => ({ id: t.id, type: t.type })),
        })),
      },
    },
  });
  return !result.isError;
}

export async function createEscalationPolicy(
  app: App,
  policy: Pick<EscalationPolicy, "name" | "description" | "num_loops" | "escalation_rules">,
): Promise<EscalationPolicy | null> {
  const result = await app.callServerTool({
    name: "create_escalation_policy",
    arguments: {
      escalation_policy: {
        name: policy.name,
        description: policy.description,
        num_loops: policy.num_loops,
        escalation_rules: policy.escalation_rules.map((r) => ({
          escalation_delay_in_minutes: r.escalation_delay_in_minutes,
          targets: r.targets.map((t) => ({ id: t.id, type: t.type })),
        })),
      },
    },
  });
  const data = extract<any>(result);
  if (!data?.id) return null;
  return mapEscalationPolicy(data);
}

export async function deleteEscalationPolicy(app: App, policyId: string): Promise<boolean> {
  const result = await app.callServerTool({
    name: "delete_escalation_policy",
    arguments: { policy_id: policyId },
  });
  return !result.isError;
}

function mapEscalationPolicy(p: any): EscalationPolicy {
  return {
    id: p.id,
    name: p.name,
    description: p.description ?? null,
    num_loops: p.num_loops ?? 0,
    escalation_rules: (p.escalation_rules ?? []).map((r: any) => ({
      id: r.id,
      escalation_delay_in_minutes: r.escalation_delay_in_minutes ?? 30,
      targets: (r.targets ?? []).map((t: any) => ({
        id: t.id,
        type: t.type as "user_reference" | "schedule_reference",
        summary: t.summary ?? t.name ?? t.id,
      })),
    })),
    services: (p.services ?? []).map((s: any) => ({ id: s.id, summary: s.summary })),
    teams: (p.teams ?? []).map((t: any) => ({ id: t.id, summary: t.summary })),
  };
}
