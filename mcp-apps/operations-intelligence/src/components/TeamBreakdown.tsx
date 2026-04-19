import type { TeamMetric } from "../api";
import { fmtMin } from "../utils";

export function TeamBreakdown({ metrics }: { metrics: TeamMetric[] }) {
  return (
    <div className="analytics-section">
      <div className="section-title">Team Performance</div>
      {metrics.length === 0 ? (
        <div className="empty-state">No team data for this period</div>
      ) : (
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Team</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">MTTA</th>
              <th className="col-num">MTTR</th>
              <th className="col-num">Escalations</th>
              <th className="col-num">Interruptions</th>
              <th className="col-num">Uptime</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((t) => (
              <tr key={t.id}>
                <td className="col-name">{t.name}</td>
                <td className="col-num">{t.totalIncidents}</td>
                <td className={`col-mono col-num${t.mttaMinutes !== null && t.mttaMinutes > 30 ? " col-warn" : ""}`}>
                  {fmtMin(t.mttaMinutes)}
                </td>
                <td className={`col-mono col-num${t.mttrMinutes !== null && t.mttrMinutes > 60 ? " col-warn" : ""}`}>
                  {fmtMin(t.mttrMinutes)}
                </td>
                <td className={`col-num${t.escalationCount > 0 ? " col-warn" : " col-ok"}`}>
                  {t.escalationCount}
                </td>
                <td className={`col-num${t.totalInterruptions > 10 ? " col-warn" : " col-ok"}`}>
                  {t.totalInterruptions}
                </td>
                <td className={`col-num${t.uptimePct === null ? "" : t.uptimePct < 99 ? " col-warn" : " col-ok"}`}>
                  {t.uptimePct !== null ? `${t.uptimePct}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
