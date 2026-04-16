/**
 * Post-Mortem Builder - API layer
 * Fetches incident data, log entries, notes, alerts, and change events.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface IncidentSummary {
  id: string;
  number: number;
  title: string;
  status: string;
  urgency: string;
  createdAt: string;
  resolvedAt: string | null;
  serviceName: string;
  priority: string | null;
  assignees: string[];
  alertCount: number;
}

export type TimelineEventKind =
  | "trigger"
  | "acknowledge"
  | "resolve"
  | "note"
  | "escalation"
  | "assign"
  | "change"
  | "alert"
  | "snooze"
  | "other";

export interface TimelineEvent {
  id: string;
  kind: TimelineEventKind;
  timestamp: string;
  summary: string;
  detail: string | null;
  actor: string | null;
  link: string | null;
}

export interface IncidentTimeline {
  incident: IncidentSummary;
  events: TimelineEvent[];
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function logEntryKind(type: string): TimelineEventKind {
  if (type.includes("trigger")) return "trigger";
  if (type.includes("acknowledge")) return "acknowledge";
  if (type.includes("resolve")) return "resolve";
  if (type.includes("annotate")) return "note";
  if (type.includes("escalat")) return "escalation";
  if (type.includes("assign") || type.includes("delegate")) return "assign";
  if (type.includes("snooze")) return "snooze";
  return "other";
}

// ─── API functions ────────────────────────────────────────────────────────────

/** List recently resolved incidents. */
export async function fetchResolvedIncidents(
  app: App,
  since: string,
  until: string
): Promise<IncidentSummary[]> {
  const result = await app.callServerTool({
    name: "list_incidents",
    arguments: {
      query_model: {
        status: ["resolved"],
        since,
        until,
        limit: 50,
      },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((i: any) => ({
    id: i.id,
    number: i.incident_number,
    title: i.title ?? i.summary,
    status: i.status,
    urgency: i.urgency,
    createdAt: i.created_at,
    resolvedAt: i.resolved_at ?? null,
    serviceName: i.service?.summary ?? i.service?.id ?? "Unknown",
    priority: i.priority?.summary ?? null,
    assignees: (i.assignments ?? []).map((a: any) => a.assignee?.summary ?? ""),
    alertCount: (i.alert_counts?.triggered ?? 0) + (i.alert_counts?.resolved ?? 0),
  }));
}

/** Fetch full incident timeline: log entries + notes + change events + alerts. */
export async function fetchIncidentTimeline(
  app: App,
  incidentId: string
): Promise<IncidentTimeline> {
  const [incResult, logResult, notesResult, changesResult, alertsResult] = await Promise.allSettled([
    app.callServerTool({ name: "get_incident", arguments: { incident_id: incidentId } }),
    app.callServerTool({ name: "list_log_entries", arguments: { query_model: { incident_id: incidentId, limit: 100 } } }),
    app.callServerTool({ name: "list_incident_notes", arguments: { incident_id: incidentId } }),
    app.callServerTool({ name: "list_incident_change_events", arguments: { incident_id: incidentId } }),
    app.callServerTool({ name: "list_alerts_from_incident", arguments: { incident_id: incidentId, query_model: { limit: 50 } } }),
  ]);

  const incData = incResult.status === "fulfilled" ? extract<any>(incResult.value) : null;
  const inc = incData?.response ?? incData ?? {};

  const logEntries: any[] = logResult.status === "fulfilled"
    ? (extract<any>(logResult.value)?.response ?? []) : [];
  const notes: any[] = notesResult.status === "fulfilled"
    ? (extract<any>(notesResult.value)?.response ?? []) : [];
  const changes: any[] = changesResult.status === "fulfilled"
    ? (extract<any>(changesResult.value)?.response ?? []) : [];
  const alerts: any[] = alertsResult.status === "fulfilled"
    ? (extract<any>(alertsResult.value)?.response ?? []) : [];

  const events: TimelineEvent[] = [];

  // Log entries
  for (const le of logEntries) {
    events.push({
      id: le.id,
      kind: logEntryKind(le.type ?? ""),
      timestamp: le.created_at,
      summary: le.summary ?? le.type,
      detail: le.note ?? le.event_details?.description ?? null,
      actor: le.agent?.summary ?? null,
      link: le.html_url ?? null,
    });
  }

  // Notes (may overlap with annotate log entries — deduplicate by content+time)
  for (const note of notes) {
    const dup = events.find(
      (e) => e.kind === "note" && e.detail === note.content && e.timestamp === note.created_at
    );
    if (!dup) {
      events.push({
        id: note.id,
        kind: "note",
        timestamp: note.created_at,
        summary: "Note added",
        detail: note.content,
        actor: note.user?.summary ?? null,
        link: null,
      });
    }
  }

  // Change events
  for (const ce of changes) {
    events.push({
      id: ce.id,
      kind: "change",
      timestamp: ce.timestamp,
      summary: ce.summary ?? "Change event",
      detail: ce.custom_details ? JSON.stringify(ce.custom_details).slice(0, 200) : null,
      actor: ce.source ?? ce.integration?.summary ?? null,
      link: ce.html_url ?? ce.links?.[0]?.href ?? null,
    });
  }

  // Alerts (only first trigger per alert key)
  const seenKeys = new Set<string>();
  for (const al of alerts) {
    const key = al.alert_key ?? al.id;
    if (!seenKeys.has(key)) {
      seenKeys.add(key);
      events.push({
        id: al.id,
        kind: "alert",
        timestamp: al.created_at,
        summary: al.summary ?? "Alert triggered",
        detail: `Severity: ${al.severity ?? "unknown"} · Status: ${al.status ?? "unknown"}`,
        actor: al.service?.summary ?? null,
        link: al.html_url ?? null,
      });
    }
  }

  // Sort chronologically
  events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  const incident: IncidentSummary = {
    id: inc.id ?? incidentId,
    number: inc.incident_number ?? 0,
    title: inc.title ?? inc.summary ?? "Unknown",
    status: inc.status ?? "resolved",
    urgency: inc.urgency ?? "low",
    createdAt: inc.created_at ?? "",
    resolvedAt: inc.resolved_at ?? null,
    serviceName: inc.service?.summary ?? "Unknown",
    priority: inc.priority?.summary ?? null,
    assignees: (inc.assignments ?? []).map((a: any) => a.assignee?.summary ?? ""),
    alertCount: (inc.alert_counts?.triggered ?? 0) + (inc.alert_counts?.resolved ?? 0),
  };

  return { incident, events };
}

/** Generate markdown export of the timeline. */
export function exportToMarkdown(timeline: IncidentTimeline): string {
  const { incident, events } = timeline;
  const duration = incident.resolvedAt
    ? Math.round(
        (new Date(incident.resolvedAt).getTime() - new Date(incident.createdAt).getTime()) / 60000
      ) + " min"
    : "ongoing";

  const lines: string[] = [
    `## Incident #${incident.number} Post-Mortem`,
    `**Title:** ${incident.title}`,
    `**Service:** ${incident.serviceName}  **Priority:** ${incident.priority ?? "—"}  **Urgency:** ${incident.urgency}  **Duration:** ${duration}`,
    "",
    "### Timeline",
    "",
  ];

  for (const ev of events) {
    const time = new Date(ev.timestamp).toLocaleString("en-US", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
    const actor = ev.actor ? ` — ${ev.actor}` : "";
    const detail = ev.detail ? `\n  > ${ev.detail.replace(/\n/g, "\n  > ")}` : "";
    lines.push(`- **${time}** — ${ev.summary}${actor}${detail}`);
  }

  lines.push("", "### Root Cause", "", "_[Fill in]_", "", "### Contributing Factors", "", "- ", "", "### Action Items", "", "- [ ] ");

  return lines.join("\n");
}
