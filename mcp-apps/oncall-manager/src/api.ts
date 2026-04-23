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

export interface OnCallShift {
  scheduleId: string;
  scheduleName: string;
  start: string;   // ISO 8601
  end: string;     // ISO 8601
  escalationLevel: number;
}

export interface Override {
  id: string;
  scheduleId: string;
  scheduleName: string;
  userId: string;
  userName: string;
  start: string;
  end: string;
}

export interface ScheduleUser {
  id: string;
  name: string;
  email: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

// ─── API functions ────────────────────────────────────────────────────────────

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
      query_model: {
        user_ids: [userId],
        since,
        until,
        earliest: false,
      },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
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
    arguments: {
      query_model: { since, until, earliest: false },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
      start: o.start,
      end: o.end,
      escalationLevel: o.escalation_level ?? 0,
    }));
}

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
  return items.map((u: any) => ({
    id: u.id,
    name: u.name ?? u.summary,
    email: u.email ?? "",
  }));
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
        overrides: [
          { start, end, user: { id: userId, type: "user_reference" } },
        ],
      },
    },
  });
  return !result.isError;
}
