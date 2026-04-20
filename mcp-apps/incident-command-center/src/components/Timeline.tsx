/**
 * Timeline - Full chronological view of all incident interactions
 */

import type { TimelineEvent } from "../api";

interface TimelineProps {
  events: TimelineEvent[];
}

const KIND_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  trigger:     { icon: "🔴", color: "#e53e3e",  label: "Alert Triggered" },
  acknowledge: { icon: "👤", color: "#d97706",  label: "Acknowledged" },
  resolve:     { icon: "✅",  color: "#38a169",  label: "Resolved" },
  note:        { icon: "📝", color: "#3182ce",  label: "Note Added" },
  escalation:  { icon: "📊", color: "#e53e3e",  label: "Escalated" },
  assign:      { icon: "↪",  color: "#805ad5",  label: "Reassigned" },
  change:      { icon: "🔧", color: "#7c3aed",  label: "Change Event" },
  alert:       { icon: "⚠️",  color: "#e53e3e",  label: "Alert" },
  snooze:      { icon: "💤", color: "#a0a0a0",  label: "Snoozed" },
  priority:    { icon: "🚨", color: "#dd6b20",  label: "Priority Changed" },
  workflow:    { icon: "⚡",  color: "#2b6cb0",  label: "Workflow" },
  other:       { icon: "●",  color: "#a0a0a0",  label: "Event" },
};

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

export function Timeline({ events }: TimelineProps) {
  return (
    <div className="timeline">
      <div className="timeline-events">
        {events.length === 0 ? (
          <p className="empty-timeline">No timeline events</p>
        ) : (
          events.map((event, idx) => {
            const cfg = KIND_CONFIG[event.kind] ?? KIND_CONFIG["other"]!;
            return (
              <div key={event.id ?? idx} className="timeline-event">
                <div className="timeline-dot" style={{ color: cfg.color }}>{cfg.icon}</div>
                <div className="timeline-line" />
                <div className="timeline-card">
                  <div className="timeline-card-header">
                    <span className="timeline-kind" style={{ color: cfg.color }}>{cfg.label}</span>
                    <span className="timeline-time">{fmt(event.timestamp)}</span>
                    {event.actor && <span className="timeline-actor">{event.actor}</span>}
                    {event.link && (
                      <a href={event.link} target="_blank" rel="noopener noreferrer" className="timeline-link">↗</a>
                    )}
                  </div>
                  <div className="timeline-summary">{event.summary}</div>
                  {event.detail && <div className="timeline-detail">{event.detail}</div>}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
