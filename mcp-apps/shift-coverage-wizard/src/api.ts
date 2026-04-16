/**
 * Shift Coverage Wizard - API layer
 * Calls PagerDuty MCP tools to fetch schedule/oncall data and create overrides.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
}

export interface ScheduleRef {
  id: string;
  name: string;
  time_zone: string;
}

export interface OnCallShift {
  scheduleId: string;
  scheduleName: string;
  start: string;
  end: string;
  escalationLevel: number;
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
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

// ─── API functions ────────────────────────────────────────────────────────────

/** Get the authenticated user's profile. */
export async function fetchCurrentUser(app: App): Promise<CurrentUser | null> {
  const result = await app.callServerTool({ name: "get_user_data", arguments: {} });
  const data = extract<any>(result);
  const user = data?.response ?? data;
  if (!user?.id) return null;
  return { id: user.id, name: user.name, email: user.email };
}

/** Get upcoming on-call shifts for a specific user within a date range. */
export async function fetchUserOnCallShifts(
  app: App,
  userId: string,
  since: string,
  until: string
): Promise<OnCallShift[]> {
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

/** Get all users on a given schedule (potential coverage candidates). */
export async function fetchScheduleUsers(
  app: App,
  scheduleId: string
): Promise<ScheduleUser[]> {
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

/** Create a schedule override. Returns true on success. */
export async function createOverride(
  app: App,
  scheduleId: string,
  userId: string,
  start: string,
  end: string
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "create_schedule_override",
    arguments: {
      schedule_id: scheduleId,
      override_request: {
        overrides: [
          {
            start,
            end,
            user: { id: userId, type: "user_reference" },
          },
        ],
      },
    },
  });
  return !result.isError;
}
