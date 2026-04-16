import type { IncidentTimeline } from "../api";
import { TimelineEventCard } from "./TimelineEvent";

interface TimelineViewProps {
  timeline: IncidentTimeline;
  onCopyMarkdown: () => void;
  onBack: () => void;
}

function durationStr(start: string, end: string | null): string {
  if (!end) return "ongoing";
  const m = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
}

export function TimelineView({ timeline, onCopyMarkdown, onBack }: TimelineViewProps) {
  const { incident, events } = timeline;
  return (
    <div className="timeline-view">
      <div className="timeline-header">
        <button className="btn btn-secondary btn-sm" onClick={onBack}>← Back</button>
        <div className="timeline-incident-meta">
          <span className="incident-number">#{incident.number}</span>
          <span className="timeline-title">{incident.title}</span>
        </div>
        <div className="timeline-incident-sub">
          <span>{incident.serviceName}</span>
          <span>·</span>
          <span>Duration: {durationStr(incident.createdAt, incident.resolvedAt)}</span>
          {incident.priority && <><span>·</span><span>{incident.priority}</span></>}
          <span>·</span>
          <span className={`badge badge-urgency badge-${incident.urgency}`}>{incident.urgency}</span>
        </div>
      </div>

      <div className="timeline-actions">
        <button className="btn btn-secondary btn-sm" onClick={onCopyMarkdown}>
          📋 Copy as Markdown
        </button>
        <span className="timeline-count">{events.length} events</span>
      </div>

      <div className="timeline-events">
        {events.length === 0 ? (
          <div className="empty-state">No timeline events found</div>
        ) : (
          events.map((ev) => <TimelineEventCard key={ev.id} event={ev} />)
        )}
      </div>
    </div>
  );
}
