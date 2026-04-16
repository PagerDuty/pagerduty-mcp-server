import type { RecentIncident } from "../api";

export type SortKey = "createdAt" | "urgency" | "status" | "mttrMinutes";

interface IncidentTableProps {
  incidents: RecentIncident[];
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function fmtMttr(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function IncidentTable({ incidents, sortKey, sortDir, onSort }: IncidentTableProps) {
  function thClass(key: SortKey): string {
    return `th-sortable${sortKey === key ? " th-active" : ""}`;
  }

  function arrow(key: SortKey): string {
    if (sortKey !== key) return " ↕";
    return sortDir === "asc" ? " ↑" : " ↓";
  }

  return (
    <div className="incident-table-wrap">
      <div className="section-title">
        Recent Incidents <span className="count-badge">{incidents.length}</span>
      </div>
      <div className="table-scroll">
        <table className="incident-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>Service</th>
              <th className={thClass("status")} onClick={() => onSort("status")}>
                Status{arrow("status")}
              </th>
              <th className={thClass("urgency")} onClick={() => onSort("urgency")}>
                Urgency{arrow("urgency")}
              </th>
              <th className={thClass("createdAt")} onClick={() => onSort("createdAt")}>
                Created{arrow("createdAt")}
              </th>
              <th className={thClass("mttrMinutes")} onClick={() => onSort("mttrMinutes")}>
                MTTR{arrow("mttrMinutes")}
              </th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((i) => (
              <tr key={i.id}>
                <td className="col-num">#{i.number}</td>
                <td className="col-title">
                  {i.priority && <span className="badge badge-priority">{i.priority}</span>}
                  {i.title}
                </td>
                <td className="col-service">{i.serviceName}</td>
                <td>
                  <span className={`badge badge-status badge-${i.status}`}>{i.status}</span>
                </td>
                <td>
                  <span className={`badge badge-urgency badge-${i.urgency}`}>{i.urgency}</span>
                </td>
                <td className="col-date">{fmt(i.createdAt)}</td>
                <td className="col-mttr">{fmtMttr(i.mttrMinutes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
