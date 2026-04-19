import type { ResponderMetric } from "../api";
import { fmtMin } from "../utils";

function fmtHours(h: number): string {
  return `${h}h`;
}

export function ResponderLoad({ metrics }: { metrics: ResponderMetric[] }) {
  return (
    <div className="analytics-section">
      <div className="section-title">Responder Load</div>
      {metrics.length === 0 ? (
        <div className="empty-state">No responder data for this period</div>
      ) : (
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Responder</th>
              <th className="col-num">On-call hrs</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">Acks</th>
              <th className="col-num">Sleep interruptions</th>
              <th className="col-num">Engaged time</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((r) => (
              <tr key={r.id}>
                <td className="col-name">
                  {r.name}
                  {r.teamName && <span className="kpi-sub"> · {r.teamName}</span>}
                </td>
                <td className="col-num col-mono">{fmtHours(r.onCallHours)}</td>
                <td className="col-num">{r.totalIncidents}</td>
                <td className="col-num">{r.totalAcks}</td>
                <td className={`col-num${r.sleepInterruptions > 0 ? " col-warn" : " col-ok"}`}>
                  {r.sleepInterruptions}
                </td>
                <td className="col-num col-mono">{fmtMin(r.engagedMinutes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
