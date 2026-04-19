import type { ServiceMetric } from "../api";

function fmtMin(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function ServiceBreakdown({ metrics }: { metrics: ServiceMetric[] }) {
  return (
    <div className="analytics-section">
      <div className="section-title">Service Performance</div>
      {metrics.length === 0 ? (
        <div className="empty-state">No service data for this period</div>
      ) : (
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Service</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">MTTA</th>
              <th className="col-num">MTTR</th>
              <th className="col-num">Escalations</th>
              <th className="col-num">Uptime</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((s) => (
              <tr key={s.id}>
                <td className="col-name">
                  {s.name}
                  {s.teamName && <span className="kpi-sub"> · {s.teamName}</span>}
                </td>
                <td className="col-num">{s.totalIncidents}</td>
                <td className={`col-mono col-num${s.mttaMinutes !== null && s.mttaMinutes > 30 ? " col-warn" : ""}`}>
                  {fmtMin(s.mttaMinutes)}
                </td>
                <td className={`col-mono col-num${s.mttrMinutes !== null && s.mttrMinutes > 60 ? " col-warn" : ""}`}>
                  {fmtMin(s.mttrMinutes)}
                </td>
                <td className={`col-num${s.escalationCount > 0 ? " col-warn" : " col-ok"}`}>
                  {s.escalationCount}
                </td>
                <td className={`col-num${s.uptimePct !== null && s.uptimePct < 99 ? " col-warn" : " col-ok"}`}>
                  {s.uptimePct !== null ? `${s.uptimePct}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
