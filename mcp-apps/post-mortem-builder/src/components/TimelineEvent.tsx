import type { TimelineEvent } from "../api";

const KIND_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  trigger:      { icon: "🔴", color: "var(--status-triggered)",    label: "Alert Triggered" },
  acknowledge:  { icon: "👤", color: "var(--status-acknowledged)",  label: "Acknowledged" },
  resolve:      { icon: "✅", color: "var(--status-resolved)",      label: "Resolved" },
  note:         { icon: "📝", color: "var(--color-note)",           label: "Note Added" },
  escalation:   { icon: "📋", color: "var(--color-escalation)",     label: "Escalated" },
  assign:       { icon: "↪",  color: "var(--color-assign)",         label: "Reassigned" },
  change:       { icon: "🔧", color: "var(--color-change)",         label: "Change Event" },
  alert:        { icon: "⚠️", color: "var(--status-triggered)",    label: "Alert" },
  snooze:       { icon: "💤", color: "var(--text-tertiary)",        label: "Snoozed" },
  other:        { icon: "●",  color: "var(--text-tertiary)",        label: "Event" },
};

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

export function TimelineEventCard({ event }: { event: TimelineEvent }) {
  const cfg = KIND_CONFIG[event.kind] ?? KIND_CONFIG["other"]!;
  return (
    <div className="timeline-event">
      <div className="timeline-dot" style={{ color: cfg.color }}>{cfg.icon}</div>
      <div className="timeline-line" />
      <div className="timeline-card">
        <div className="timeline-card-header">
          <span className="timeline-kind" style={{ color: cfg.color }}>{cfg.label}</span>
          <span className="timeline-time">{fmt(event.timestamp)}</span>
          {event.actor && <span className="timeline-actor">{event.actor}</span>}
          {event.link && (
            <a href={event.link} target="_blank" rel="noopener noreferrer" className="timeline-link">
              ↗
            </a>
          )}
        </div>
        <div className="timeline-summary">{event.summary}</div>
        {event.detail && <div className="timeline-detail">{event.detail}</div>}
      </div>
    </div>
  );
}
