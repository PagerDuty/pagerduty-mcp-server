import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { fetchIncidentDetails, createStatusUpdate } from "../api";

interface Props {
  app: App;
  incident: {
    id: string;
    incident_number: number;
    title: string;
    status: string;
    urgency: string;
    service: { summary: string };
    priority?: { summary: string };
    assignments?: Array<{ assignee: { summary: string } }>;
    created_at: string;
  };
  onClose: () => void;
  onSubmitted: () => void;
}

function durationStr(isoStart: string): string {
  const ms = Date.now() - new Date(isoStart).getTime();
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function buildDraft(incident: Props["incident"], details: any): string {
  const inc = details.incident ?? incident;
  const events: any[] = details.timelineEvents ?? [];
  const notes: any[] = details.notes ?? [];
  const alerts: any[] = details.alerts ?? [];

  const statusLabel =
    inc.status === "triggered"
      ? "Investigating"
      : inc.status === "acknowledged"
        ? "Identified / In Progress"
        : "Resolved";

  // Full timeline — every event
  const timelineLines = events.map((e: any) => {
    const t = new Date(e.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const actor = e.actor ? ` (${e.actor})` : "";
    const detail = e.detail ? `: ${String(e.detail).slice(0, 200)}` : "";
    return `  [${t}] ${e.summary}${actor}${detail}`;
  });

  // All notes
  const noteLines = notes.map(
    (n: any) => `  • ${n.user?.summary ?? "Unknown"}: ${n.content}`
  );

  // All alerts
  const alertLines = alerts.map(
    (a: any) =>
      `  • ${a.summary ?? a.alert_key ?? "Alert"} — ${a.status ?? "unknown"}, severity: ${a.severity ?? "unknown"}`
  );

  return [
    `Status Update — Incident #${inc.incident_number ?? incident.incident_number}`,
    `Status: ${statusLabel}`,
    `Service: ${inc.service?.summary ?? incident.service.summary}`,
    inc.priority?.summary ? `Priority: ${inc.priority.summary}` : null,
    `Urgency: ${inc.urgency ?? incident.urgency}`,
    `Assigned to: ${inc.assignments?.[0]?.assignee?.summary ?? "Unassigned"}`,
    `Duration: ${durationStr(inc.created_at ?? incident.created_at)}`,
    "",
    `Incident: ${inc.title ?? incident.title}`,
    "",
    `── Timeline (${events.length} events) ──`,
    ...(timelineLines.length ? timelineLines : ["  No events recorded."]),
    "",
    `── Notes (${notes.length}) ──`,
    ...(noteLines.length ? noteLines : ["  No notes."]),
    "",
    `── Alerts (${alerts.length}) ──`,
    ...(alertLines.length ? alertLines : ["  No alerts."]),
    "",
    "Next update will be provided in 30 minutes or when there is a significant change.",
  ]
    .filter((l) => l !== null)
    .join("\n");
}

export function StatusUpdateModal({ app, incident, onClose, onSubmitted }: Props) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchIncidentDetails(app, incident.id)
      .then((details) => {
        if (cancelled) return;
        setMessage(buildDraft(incident, details ?? {}));
      })
      .catch(() => {
        if (cancelled) return;
        setMessage(buildDraft(incident, {}));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [app, incident.id]);

  async function handleSubmit() {
    if (!message.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await createStatusUpdate(app, incident.id, message.trim());
      onSubmitted();
    } catch (err: any) {
      setError(err?.message ?? "Failed to post status update");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog status-update-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>📢 AI Status Update — #{incident.incident_number}</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <p className="status-update-hint">
            Generated from the full incident timeline. Edit as needed, then submit.
          </p>

          {loading ? (
            <div className="status-update-loading">
              <span className="spinner-sm" /> Building from timeline…
            </div>
          ) : (
            <textarea
              className="status-update-textarea"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={18}
              disabled={submitting}
            />
          )}

          {error && <p className="status-update-error">{error}</p>}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={loading || submitting || !message.trim()}
          >
            {submitting ? "Posting…" : "Submit Status Update"}
          </button>
        </div>
      </div>
    </div>
  );
}
