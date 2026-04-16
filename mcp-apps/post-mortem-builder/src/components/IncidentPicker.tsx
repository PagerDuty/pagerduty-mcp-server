import type { IncidentSummary } from "../api";

interface IncidentPickerProps {
  incidents: IncidentSummary[];
  onSelect: (id: string) => void;
  search: string;
  onSearchChange: (v: string) => void;
  urgencyFilter: string;
  onUrgencyChange: (v: string) => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

function durationStr(start: string, end: string | null): string {
  if (!end) return "ongoing";
  const m = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
}

export function IncidentPicker({
  incidents, onSelect, search, onSearchChange, urgencyFilter, onUrgencyChange,
}: IncidentPickerProps) {
  const filtered = incidents.filter((i) => {
    const matchSearch =
      !search ||
      i.title.toLowerCase().includes(search.toLowerCase()) ||
      i.serviceName.toLowerCase().includes(search.toLowerCase()) ||
      String(i.number).includes(search);
    const matchUrgency = !urgencyFilter || i.urgency === urgencyFilter;
    return matchSearch && matchUrgency;
  });

  return (
    <div className="incident-picker">
      <div className="picker-controls">
        <input
          type="search"
          placeholder="Search incidents..."
          value={search}
          onChange={(e) => onSearchChange(e.currentTarget.value)}
          className="picker-search"
        />
        <select
          value={urgencyFilter}
          onChange={(e) => onUrgencyChange(e.currentTarget.value)}
          className="picker-filter"
        >
          <option value="">All urgencies</option>
          <option value="high">High</option>
          <option value="low">Low</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">No incidents found</div>
      ) : (
        <div className="incident-list">
          {filtered.map((i) => (
            <div key={i.id} className="incident-row">
              <div className="incident-row-main">
                <span className="incident-number">#{i.number}</span>
                <span className="incident-title">{i.title}</span>
                {i.priority && <span className="badge badge-priority">{i.priority}</span>}
                <span className={`badge badge-urgency badge-${i.urgency}`}>{i.urgency}</span>
              </div>
              <div className="incident-row-meta">
                <span>{i.serviceName}</span>
                <span>·</span>
                <span>{fmt(i.createdAt)}</span>
                <span>·</span>
                <span>{durationStr(i.createdAt, i.resolvedAt)}</span>
                {i.alertCount > 0 && (
                  <>
                    <span>·</span>
                    <span>{i.alertCount} alert{i.alertCount !== 1 ? "s" : ""}</span>
                  </>
                )}
              </div>
              <button className="btn btn-primary btn-sm" onClick={() => onSelect(i.id)}>
                Build Post-Mortem
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
