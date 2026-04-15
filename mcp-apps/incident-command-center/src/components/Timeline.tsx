/**
 * Timeline - Chronological view of incident events (notes, alerts, changes)
 */

import { useMemo } from "react";

interface TimelineNote {
  id: string;
  type: "note";
  content: string;
  created_at: string;
  user: {
    summary: string;
  };
}

interface TimelineAlert {
  id: string;
  type: "alert";
  summary: string;
  created_at: string;
  status: string;
}

interface TimelineChange {
  id: string;
  type: "change";
  summary: string;
  timestamp: string;
}

type TimelineEvent = TimelineNote | TimelineAlert | TimelineChange;

interface TimelineProps {
  notes: any[];
  alerts: any[];
  changes: any[];
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString();
}

function getEventTime(event: TimelineEvent): string {
  if ("timestamp" in event) return event.timestamp;
  return event.created_at;
}

export function Timeline({ notes, alerts, changes }: TimelineProps) {
  const events = useMemo(() => {
    const allEvents: TimelineEvent[] = [
      ...notes.map((n) => ({ ...n, type: "note" as const })),
      ...alerts.map((a) => ({ ...a, type: "alert" as const })),
      ...changes.map((c) => ({ ...c, type: "change" as const })),
    ];

    // Sort by timestamp (newest first)
    return allEvents.sort((a, b) => {
      const timeA = new Date(getEventTime(a)).getTime();
      const timeB = new Date(getEventTime(b)).getTime();
      return timeB - timeA;
    });
  }, [notes, alerts, changes]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case "note":
        return "📝";
      case "alert":
        return "🔔";
      case "change":
        return "🔄";
      default:
        return "•";
    }
  };

  const getEventClass = (type: string) => {
    return `timeline-event event-${type}`;
  };

  return (
    <div className="timeline">
      <h4>⏱️ Incident Timeline</h4>

      <div className="timeline-events">
        {events.length === 0 ? (
          <p className="empty-timeline">No timeline events</p>
        ) : (
          events.map((event) => (
            <div key={event.id} className={getEventClass(event.type)}>
              <div className="timeline-marker">
                <span className="timeline-icon">{getEventIcon(event.type)}</span>
                <div className="timeline-line"></div>
              </div>

              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="timeline-type">{event.type.toUpperCase()}</span>
                  <span className="timeline-time">{formatTimestamp(getEventTime(event))}</span>
                </div>

                {event.type === "note" && (
                  <div className="timeline-note">
                    <strong>{event.user.summary}</strong>
                    <p>{event.content}</p>
                  </div>
                )}

                {event.type === "alert" && (
                  <div className="timeline-alert">
                    <p>{event.summary}</p>
                    <span className={`status-badge status-${event.status}`}>
                      {event.status}
                    </span>
                  </div>
                )}

                {event.type === "change" && (
                  <div className="timeline-change">
                    <p>{event.summary}</p>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
