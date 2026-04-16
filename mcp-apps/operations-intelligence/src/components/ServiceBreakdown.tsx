import type { ServiceStat } from "../api";

function fmtMttr(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function ServiceBreakdown({ stats, max }: { stats: ServiceStat[]; max: number }) {
  return (
    <div className="service-breakdown">
      <div className="section-title">Incidents by Service</div>
      {stats.length === 0 ? (
        <div className="empty-state">No service data</div>
      ) : (
        <table className="service-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Incidents</th>
              <th>High Urgency</th>
              <th>MTTR</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((s) => (
              <tr key={s.id}>
                <td className="service-name">{s.name}</td>
                <td>
                  <div className="bar-cell">
                    <div
                      className="bar-fill"
                      style={{ width: `${Math.round((s.incidentCount / max) * 100)}%` }}
                    />
                    <span>{s.incidentCount}</span>
                  </div>
                </td>
                <td>
                  {s.highUrgencyCount > 0 ? (
                    <span className="high-urgency-count">{s.highUrgencyCount}</span>
                  ) : (
                    <span className="zero-count">0</span>
                  )}
                </td>
                <td className="mttr-cell">{fmtMttr(s.mttrMinutes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
